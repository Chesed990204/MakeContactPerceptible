// using UnityEngine;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;

// public class TCPClient : MonoBehaviour
// {
//     TcpClient client;
//     NetworkStream stream;
//     public string serverIP = "127.0.0.1";
//     public int serverPort = 25001;

//     public Leap.CustomCapsuleHand RightHand;

//     private Thread sendThread;
//     private bool isRunning = false;

//     private bool sendingActive = false;

//     public int num_trial = 0;
//     private Leap.CustomCapsuleHand.MotionState prevState = Leap.CustomCapsuleHand.MotionState.None;

//     void Start()
//     {
//         client = new TcpClient();
//         client.Connect(serverIP, serverPort);
//         stream = client.GetStream();

//         isRunning = true;
//         sendThread = new Thread(SendLoop);
//         sendThread.IsBackground = true;
//         sendThread.Start();
//     }

//     void SendLoop()
//     {
//         while (isRunning)
//     {
//         if (RightHand == null) continue;

//         var state = RightHand.currentState;

//         if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
//         {
//             sendingActive = true;
//             Debug.Log("Start detected - begin sending.");
//         }

//         if (sendingActive)
//         {
//             SendTwoPositions(state);

//                 if (state == Leap.CustomCapsuleHand.MotionState.End)
//                 {
//                     Debug.Log("End detected - stop sending.");
//                     sendingActive = false;
//                     num_trial += 1;
//                     Debug.Log(num_trial);
//             }
//         }

//         Thread.Sleep(10);
//     }
//     }

//     void SendTwoPositions(Leap.CustomCapsuleHand.MotionState state)
//     {
//         if (RightHand == null) return;

//        Vector3 pos1 = RightHand.palm_position;
//         Vector3 pos2 = RightHand.index_position;

//     string message = $"{pos1.x},{pos1.y},{pos1.z}|{pos2.x},{pos2.y},{pos2.z}|{state}";
//     byte[] data = Encoding.UTF8.GetBytes(message);

//     try
//     {
//         lock (stream)
//         {
//             stream.Write(data, 0, data.Length);
//             byte[] buffer = new byte[1024];
//             int bytesRead = stream.Read(buffer, 0, buffer.Length);
//             string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
//             Debug.Log("Python Response: " + response);
//         }
//     }
//     catch (SocketException e)
//     {
//         Debug.LogError("Socket error: " + e.Message);
//         isRunning = false;
//     }
//     }

//     void OnApplicationQuit()
//     {
//         isRunning = false;
//         sendThread?.Join();

//         stream?.Close();
//         client?.Close();
//     }
// }
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Generic;

public class TCPClient : MonoBehaviour
{
    TcpClient client;
    NetworkStream stream;
    public string serverIP = "127.0.0.1";
    public int serverPort = 25001;

    public Leap.CustomCapsuleHand RightHand;

    private Thread sendThread;
    private bool isRunning = false;

    private bool sendingActive = false;

    public int num_trial = 0;
    private Leap.CustomCapsuleHand.MotionState prevState = Leap.CustomCapsuleHand.MotionState.None;

    private List<float> indexZSequence = new List<float>();

    void Start()
    {
        client = new TcpClient();
        client.Connect(serverIP, serverPort);
        stream = client.GetStream();

        isRunning = true;
        sendThread = new Thread(SendLoop);
        sendThread.IsBackground = true;
        sendThread.Start();
    }

    void SendLoop()
    {
        while (isRunning)
        {
            if (RightHand == null) continue;

            var state = RightHand.currentState;

            if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
            {
                sendingActive = true;
                indexZSequence.Clear();
                Debug.Log("Start detected - begin sending.");
            }

            if (sendingActive)
            {
                indexZSequence.Add(RightHand.index_position.z);

                if (state == Leap.CustomCapsuleHand.MotionState.End)
                {
                    Debug.Log("End detected - stop sending.");
                    sendingActive = false;
                    num_trial += 1;
                    SendTrialData();
                }
            }

            Thread.Sleep(10);
        }
    }

    void SendTrialData()
    {
        float maxZ = RightHand.trialMaxIndexZList.Count > 0 ? 
            RightHand.trialMaxIndexZList[RightHand.trialMaxIndexZList.Count - 1] : -999f;

        float impact = RightHand.impact_position;
        float error = maxZ - 0.1293f;  // GROUND_TRUTH

        string zSequenceStr = string.Join(",", indexZSequence);

        string message = $"trial:{num_trial}|indexZs:[{zSequenceStr}]|maxZ:{maxZ}|impact:{impact}|error:{error}";
        byte[] data = Encoding.UTF8.GetBytes(message);

        try
        {
            lock (stream)
            {
                stream.Write(data, 0, data.Length);
                byte[] buffer = new byte[1024];
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                Debug.Log("Python Response: " + response);
            }
        }
        catch (SocketException e)
        {
            Debug.LogError("Socket error: " + e.Message);
            isRunning = false;
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        sendThread?.Join();
        stream?.Close();
        client?.Close();
    }
}
