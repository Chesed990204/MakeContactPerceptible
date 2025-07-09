// TCPClient.cs
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Generic;

public class TCPClient : MonoBehaviour
{
    [SerializeField]
    public GameObject button;

    private TcpClient trialClient;
    private NetworkStream trialStream;
    public string serverIP = "127.0.0.1";
    public int trialServerPort = 25001;

    public RealtimeTCPClient RealtimeClientInstance;

    public Leap.CustomCapsuleHand RightHand;
    public CustomFeedbackProvider FeedbackProvider;

    private Thread trialSendThread;
    private volatile bool trialIsRunning = false; // Use volatile for thread safety

    private bool sendingActive = false;

    public int num_trial = 0;

    private List<float> indexZSequence = new List<float>();

    void Start()
    {
        // Connection logic is now handled in TrialSendLoop
        trialIsRunning = true; // Set to true to start the loop
        trialSendThread = new Thread(TrialSendLoop);
        trialSendThread.IsBackground = true;
        trialSendThread.Start();
        Debug.Log($"TCPClient (Trial) thread started for {serverIP}:{trialServerPort}");

        if (RealtimeClientInstance == null)
        {
            RealtimeClientInstance = FindObjectOfType<RealtimeTCPClient>();
            if (RealtimeClientInstance == null)
            {
                Debug.LogError("RealtimeTCPClient instance not found in the scene. Please add it to a GameObject.");
            }
        }

        FeedbackProvider = button.GetComponent<CustomFeedbackProvider>();
        if (FeedbackProvider == null)
        {
            Debug.LogError("CustomFeedbackProvider not found on the assigned button GameObject.");
        }
    }

    void TrialSendLoop()
    {
        while (trialIsRunning)
        {
            // Reconnection logic: Check if client is connected; if not, try to connect
            if (trialClient == null || !trialClient.Connected)
            {
                // Ensure any previous broken connections are properly closed
                if (trialStream != null) { try { trialStream.Close(); } catch { } trialStream = null; }
                if (trialClient != null) { try { trialClient.Close(); } catch { } trialClient = null; }

                Debug.LogWarning("TCPClient (Trial): Not connected. Attempting to reconnect...");
                try
                {
                    trialClient = new TcpClient();
                    trialClient.Connect(serverIP, trialServerPort);
                    trialStream = trialClient.GetStream();
                    Debug.Log($"TCPClient (Trial) reconnected to {serverIP}:{trialServerPort}");
                }
                catch (SocketException e)
                {
                    Debug.LogError($"TCPClient (Trial) reconnection failed: {e.Message}. Retrying in 1 second.");
                    Thread.Sleep(1000); // Wait before retrying
                    continue; // Skip the rest of the loop and re-check connection
                }
            }

            if (RightHand == null || FeedbackProvider == null)
            {
                Thread.Sleep(100);
                continue;
            }

            var state = RightHand.currentState;
            if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
            {
                sendingActive = true;
                indexZSequence.Clear();
                Debug.Log("Trial data buffering started.");
            }

            if (sendingActive)
            {
                indexZSequence.Add(RightHand.index_position.z);

                if (state == Leap.CustomCapsuleHand.MotionState.End)
                {
                    Debug.Log("Trial data buffering ended. Sending trial data.");
                    sendingActive = false;
                    num_trial += 1;
                    SendTrialData(); // Call SendTrialData to actually send
                }
            }

            Thread.Sleep(10);
        }
        Debug.Log("TCPClient (Trial) SendLoop finished.");
    }

    void SendTrialData()
    {
        // Check connection state before attempting to send.
        // If not connected, rely on TrialSendLoop to re-establish.
        if (trialClient == null || !trialClient.Connected || trialStream == null)
        {
            Debug.LogError("Trial client not connected when trying to send data. Skipping send for this trial, reconnect will be attempted by loop.");
            // Close existing invalid state to allow reconnection logic in TrialSendLoop to take over
            if (trialStream != null) { try { trialStream.Close(); } catch { } trialStream = null; }
            if (trialClient != null) { try { trialClient.Close(); } catch { } trialClient = null; }
            return; // Exit without attempting to send
        }

        float maxZ = RightHand.trialMaxIndexZList.Count > 0 ?
            RightHand.trialMaxIndexZList[RightHand.trialMaxIndexZList.Count - 1] : -999f;

        float impact = RightHand.impact_position;
        float error = maxZ - RightHand.GROUND_TRUTH;

        string zSequenceStr = string.Join(",", indexZSequence);

        string feedbackType = FeedbackProvider._feedbackPreset.ToString();

        string message = $"trial:{num_trial}|indexZs:[{zSequenceStr}]|maxZ:{maxZ}|impact:{impact}|error:{error}|feedbackType:{feedbackType}\n";

        byte[] data = Encoding.UTF8.GetBytes(message);

        try
        {
            lock (trialStream)
            {
                trialStream.Write(data, 0, data.Length);
                byte[] buffer = new byte[1024];
                int bytesRead = trialStream.Read(buffer, 0, buffer.Length);
                string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                Debug.Log("Python Trial Response: " + response);

                if (response.Contains("OK") && !response.Contains("DISCARDED"))
                {
                    RightHand.RecordTrialOutcome(error, true);
                    Debug.Log("Adaptive is working!@!");
                }
                else if (response.Contains("DISCARDED"))
                {
                    RightHand.RecordTrialOutcome(error, false);
                }
            }
        }
        catch (SocketException e)
        {
            Debug.LogError("Trial Socket error during send/receive: " + e.Message + ". Closing connection to force reconnect.");
            if (trialStream != null) { try { trialStream.Close(); } catch { } trialStream = null; }
            if (trialClient != null) { try { trialClient.Close(); } catch { } trialClient = null; }
            // DO NOT set trialIsRunning = false;
        }
        catch (System.ObjectDisposedException)
        {
            Debug.LogWarning("Trial stream/client disposed during write. Closing connection to force reconnect.");
            if (trialStream != null) { try { trialStream.Close(); } catch { } trialStream = null; }
            if (trialClient != null) { try { trialClient.Close(); } catch { } trialClient = null; }
            // DO NOT set trialIsRunning = false;
        }
        catch (System.Exception e)
        {
            Debug.LogError("Trial SendData unexpected error: " + e.Message + ". Closing connection to force reconnect.");
            if (trialStream != null) { try { trialStream.Close(); } catch { } trialStream = null; }
            if (trialClient != null) { try { trialClient.Close(); } catch { } trialClient = null; }
            // DO NOT set trialIsRunning = false;
        }
    }

    void OnApplicationQuit()
    {
        trialIsRunning = false;
        if (trialSendThread != null && trialSendThread.IsAlive) trialSendThread.Join();
        if (trialStream != null) trialStream.Close();
        if (trialClient != null) trialClient.Close();
        Debug.Log("TCPClient (Trial) connections closed.");
    }
}