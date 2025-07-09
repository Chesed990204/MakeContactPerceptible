// RealtimeTCPClient.cs
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;

public class RealtimeTCPClient : MonoBehaviour
{
    private TcpClient realTimeClient;
    private NetworkStream realTimeStream;
    public string serverIP = "127.0.0.1";
    public int realTimeServerPort = 25002;

    private Thread realTimeSendThread;
    private volatile bool realTimeIsRunning = false; // Use volatile for thread safety

    private ConcurrentQueue<bool> vibroConditionQueue = new ConcurrentQueue<bool>();
    private bool lastSentVibroCondition = false;

    [Tooltip("True 신호가 최소한으로 유지될 시간 (초)")]
    public float minTrueDuration = 0.05f;
    private float trueConditionStartTime = -1f;
    private bool pendingTrueCondition = false;


    void Start()
    {
        // Connection logic is now handled in RealTimeSendLoop
        realTimeIsRunning = true; // Set to true to start the loop
        realTimeSendThread = new Thread(RealTimeSendLoop);
        realTimeSendThread.IsBackground = true;
        realTimeSendThread.Start();
        Debug.Log($"RealtimeTCPClient thread started for {serverIP}:{realTimeServerPort}");
    }

    public void EnqueueVibroCondition(bool condition)
    {
        if (condition)
        {
            pendingTrueCondition = true;
            trueConditionStartTime = Time.time;
            if (!lastSentVibroCondition)
            {
                vibroConditionQueue.Enqueue(true);
            }
            lastSentVibroCondition = true;
        }
        else
        {
            if (pendingTrueCondition && Time.time - trueConditionStartTime < minTrueDuration)
            {
                // Still within minTrueDuration, ignore False
            }
            else
            {
                if (lastSentVibroCondition)
                {
                    vibroConditionQueue.Enqueue(false);
                }
                lastSentVibroCondition = false;
                pendingTrueCondition = false;
            }
        }
    }

    void RealTimeSendLoop()
    {
        while (realTimeIsRunning)
        {
            // Reconnection logic: Check if client is connected; if not, try to connect
            if (realTimeClient == null || !realTimeClient.Connected)
            {
                // Ensure any previous broken connections are properly closed
                if (realTimeStream != null) { try { realTimeStream.Close(); } catch { } realTimeStream = null; }
                if (realTimeClient != null) { try { realTimeClient.Close(); } catch { } realTimeClient = null; }

                Debug.LogWarning("RealtimeTCPClient: Not connected. Attempting to reconnect...");
                try
                {
                    realTimeClient = new TcpClient();
                    realTimeClient.Connect(serverIP, realTimeServerPort);
                    realTimeStream = realTimeClient.GetStream();
                    Debug.Log($"RealtimeTCPClient reconnected to {serverIP}:{realTimeServerPort}");
                }
                catch (SocketException e)
                {
                    Debug.LogError($"RealtimeTCPClient reconnection failed: {e.Message}. Retrying in 1 second.");
                    Thread.Sleep(1000); // Wait before retrying
                    continue; // Skip the rest of the loop and re-check connection
                }
            }

            bool conditionToSend;
            if (!vibroConditionQueue.IsEmpty)
            {
                if (vibroConditionQueue.TryDequeue(out bool newCondition))
                {
                    conditionToSend = newCondition;
                }
                else
                {
                    conditionToSend = lastSentVibroCondition;
                }
            }
            else
            {
                conditionToSend = lastSentVibroCondition;
            }

            string message = $"vibroCondition:{conditionToSend}\n";
            Debug.LogFormat("Realtime Client says: {0}", conditionToSend);
            byte[] data = Encoding.UTF8.GetBytes(message);

            try
            {
                lock (realTimeStream)
                {
                    realTimeStream.Write(data, 0, data.Length);
                }
            }
            catch (SocketException e)
            {
                Debug.LogError("RealtimeTCPClient Socket error during send/receive: " + e.Message + ". Closing connection to force reconnect.");
                // Close current invalid state to allow reconnection logic in next loop iteration
                if (realTimeStream != null) { try { realTimeStream.Close(); } catch { } realTimeStream = null; }
                if (realTimeClient != null) { try { realTimeClient.Close(); } catch { } realTimeClient = null; }
                continue; // Go to the next iteration to attempt reconnect
            }
            catch (System.ObjectDisposedException)
            {
                Debug.LogWarning("RealtimeTCPClient stream/client disposed during write. Closing connection to force reconnect.");
                if (realTimeStream != null) { try { realTimeStream.Close(); } catch { } realTimeStream = null; }
                if (realTimeClient != null) { try { realTimeClient.Close(); } catch { } realTimeClient = null; }
                continue;
            }
            catch (System.Exception e)
            {
                Debug.LogError("RealtimeTCPClient SendLoop unexpected error: " + e.Message + ". Closing connection to force reconnect.");
                if (realTimeStream != null) { try { realTimeStream.Close(); } catch { } realTimeStream = null; }
                if (realTimeClient != null) { try { realTimeClient.Close(); } catch { } realTimeClient = null; }
                continue;
            }

            Thread.Sleep(16);
        }
        Debug.Log("RealtimeTCPClient SendLoop finished.");
    }

    void OnApplicationQuit()
    {
        realTimeIsRunning = false;
        if (realTimeSendThread != null && realTimeSendThread.IsAlive)
        {
            realTimeSendThread.Join();
        }
        if (realTimeStream != null)
        {
            realTimeStream.Close();
            realTimeStream = null;
        }
        if (realTimeClient != null)
        {
            realTimeClient.Close();
            realTimeClient = null;
        }
        Debug.Log("RealtimeTCPClient connections closed.");
    }
}