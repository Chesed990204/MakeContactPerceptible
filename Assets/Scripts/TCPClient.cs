// // using UnityEngine;
// // using System.Net.Sockets;
// // using System.Text;
// // using System.Threading;

// // public class TCPClient : MonoBehaviour
// // {
// //     TcpClient client;
// //     NetworkStream stream;
// //     public string serverIP = "127.0.0.1";
// //     public int serverPort = 25001;

// //     public Leap.CustomCapsuleHand RightHand;

// //     private Thread sendThread;
// //     private bool isRunning = false;

// //     private bool sendingActive = false;

// //     public int num_trial = 0;
// //     private Leap.CustomCapsuleHand.MotionState prevState = Leap.CustomCapsuleHand.MotionState.None;

// //     void Start()
// //     {
// //         client = new TcpClient();
// //         client.Connect(serverIP, serverPort);
// //         stream = client.GetStream();

// //         isRunning = true;
// //         sendThread = new Thread(SendLoop);
// //         sendThread.IsBackground = true;
// //         sendThread.Start();
// //     }

// //     void SendLoop()
// //     {
// //         while (isRunning)
// //     {
// //         if (RightHand == null) continue;

// //         var state = RightHand.currentState;

// //         if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
// //         {
// //             sendingActive = true;
// //             Debug.Log("Start detected - begin sending.");
// //         }

// //         if (sendingActive)
// //         {
// //             SendTwoPositions(state);

// //                 if (state == Leap.CustomCapsuleHand.MotionState.End)
// //                 {
// //                     Debug.Log("End detected - stop sending.");
// //                     sendingActive = false;
// //                     num_trial += 1;
// //                     Debug.Log(num_trial);
// //             }
// //         }

// //         Thread.Sleep(10);
// //     }
// //     }

// //     void SendTwoPositions(Leap.CustomCapsuleHand.MotionState state)
// //     {
// //         if (RightHand == null) return;

// //        Vector3 pos1 = RightHand.palm_position;
// //         Vector3 pos2 = RightHand.index_position;

// //     string message = $"{pos1.x},{pos1.y},{pos1.z}|{pos2.x},{pos2.y},{pos2.z}|{state}";
// //     byte[] data = Encoding.UTF8.GetBytes(message);

// //     try
// //     {
// //         lock (stream)
// //         {
// //             stream.Write(data, 0, data.Length);
// //             byte[] buffer = new byte[1024];
// //             int bytesRead = stream.Read(buffer, 0, buffer.Length);
// //             string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
// //             Debug.Log("Python Response: " + response);
// //         }
// //     }
// //     catch (SocketException e)
// //     {
// //         Debug.LogError("Socket error: " + e.Message);
// //         isRunning = false;
// //     }
// //     }

// //     void OnApplicationQuit()
// //     {
// //         isRunning = false;
// //         sendThread?.Join();

// //         stream?.Close();
// //         client?.Close();
// //     }
// // }
// // using UnityEngine;
// // using System.Net.Sockets;
// // using System.Text;
// // using System.Threading;
// // using System.Collections.Generic;

// // public class TCPClient : MonoBehaviour
// // {
// //     TcpClient client;
// //     NetworkStream stream;
// //     public string serverIP = "127.0.0.1";
// //     public int serverPort = 25001;

// //     public Leap.CustomCapsuleHand RightHand;

// //     private Thread sendThread;
// //     private bool isRunning = false;

// //     private bool sendingActive = false;

// //     public int num_trial = 0;
// //     private Leap.CustomCapsuleHand.MotionState prevState = Leap.CustomCapsuleHand.MotionState.None;

// //     private List<float> indexZSequence = new List<float>();

// //     void Start()
// //     {
// //         client = new TcpClient();
// //         client.Connect(serverIP, serverPort);
// //         stream = client.GetStream();

// //         isRunning = true;
// //         sendThread = new Thread(SendLoop);
// //         sendThread.IsBackground = true;
// //         sendThread.Start();
// //     }

// //     void SendLoop()
// //     {
// //         while (isRunning)
// //         {
// //             if (RightHand == null) continue;

// //             var state = RightHand.currentState;

// //             if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
// //             {
// //                 sendingActive = true;
// //                 indexZSequence.Clear();
// //                 Debug.Log("Start detected - begin sending.");
// //             }

// //             if (sendingActive)
// //             {
// //                 indexZSequence.Add(RightHand.index_position.z);

// //                 if (state == Leap.CustomCapsuleHand.MotionState.End)
// //                 {
// //                     Debug.Log("End detected - stop sending.");
// //                     sendingActive = false;
// //                     num_trial += 1;
// //                     SendTrialData();
// //                 }
// //             }

// //             Thread.Sleep(10);
// //         }
// //     }

// //     void SendTrialData()
// //     {
// //         float maxZ = RightHand.trialMaxIndexZList.Count > 0 ? 
// //             RightHand.trialMaxIndexZList[RightHand.trialMaxIndexZList.Count - 1] : -999f;

// //         float impact = RightHand.impact_position;
// //         float error = maxZ - 0.1293f;  // GROUND_TRUTH

// //         string zSequenceStr = string.Join(",", indexZSequence);

// //         string message = $"trial:{num_trial}|indexZs:[{zSequenceStr}]|maxZ:{maxZ}|impact:{impact}|error:{error}";
// //         byte[] data = Encoding.UTF8.GetBytes(message);

// //         try
// //         {
// //             lock (stream)
// //             {
// //                 stream.Write(data, 0, data.Length);
// //                 byte[] buffer = new byte[1024];
// //                 int bytesRead = stream.Read(buffer, 0, buffer.Length);
// //                 string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
// //                 Debug.Log("Python Response: " + response);
// //             }
// //         }
// //         catch (SocketException e)
// //         {
// //             Debug.LogError("Socket error: " + e.Message);
// //             isRunning = false;
// //         }
// //     }

// //     void OnApplicationQuit()
// //     {
// //         isRunning = false;
// //         sendThread?.Join();
// //         stream?.Close();
// //         client?.Close();
// //     }
// // }

// // TCPClient.cs
// using UnityEngine;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;
// using System.Collections.Generic;

// public class TCPClient : MonoBehaviour
// {
//     [SerializeField]
//     public GameObject button;
//     TcpClient client;
//     NetworkStream stream;
//     public string serverIP = "127.0.0.1";
//     public int serverPort = 25001;

//     public Leap.CustomCapsuleHand RightHand;
//     public CustomFeedbackProvider FeedbackProvider; // CustomFeedbackProvider 참조 추가'

    

//     private Thread sendThread;
//     private bool isRunning = false;

//     private bool sendingActive = false;

//     public int num_trial = 0;
//     private Leap.CustomCapsuleHand.MotionState prevState = Leap.CustomCapsuleHand.MotionState.None;

//     private List<float> indexZSequence = new List<float>();

//     void Start()
//     {
//         client = new TcpClient();
//         client.Connect(serverIP, serverPort);
//         stream = client.GetStream();
//         FeedbackProvider = button.GetComponent<CustomFeedbackProvider>();
//         isRunning = true;
//         sendThread = new Thread(SendLoop);
//         sendThread.IsBackground = true;
//         sendThread.Start();
//     }

//     void SendLoop()
//     {
//         while (isRunning)
//         {
//             if (RightHand == null || FeedbackProvider == null) continue; // FeedbackProvider null 체크 추가

//             var state = RightHand.currentState;
//             Debug.LogFormat("Sending active: {0}", state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive);
//             if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
//             {
//                 sendingActive = true;
//                 indexZSequence.Clear();
//                 Debug.Log("Start detected - begin sending.");
//             }

//             if (sendingActive)
//             {
//                 indexZSequence.Add(RightHand.index_position.z);

//                 if (state == Leap.CustomCapsuleHand.MotionState.End)
//                 {
//                     Debug.Log("End detected - stop sending.");
//                     sendingActive = false;
//                     num_trial += 1;
//                     SendTrialData();
//                 }
//             }

//             Thread.Sleep(10);
//         }
//     }

//     void SendTrialData()
//     {
//         float maxZ = RightHand.trialMaxIndexZList.Count > 0 ? 
//             RightHand.trialMaxIndexZList[RightHand.trialMaxIndexZList.Count - 1] : -999f;

//         float impact = RightHand.impact_position;
//         float error = maxZ - RightHand.GROUND_TRUTH; // GROUND_TRUTH는 CustomCapsuleHand에 public으로 노출되어야 합니다.

//         string zSequenceStr = string.Join(",", indexZSequence);

//         // FeedbackType을 메시지에 포함
//         string feedbackType = FeedbackProvider._feedbackPreset.ToString(); 
//         string message = $"trial:{num_trial}|indexZs:[{zSequenceStr}]|maxZ:{maxZ}|impact:{impact}|error:{error}|feedbackType:{feedbackType}\n"; // 줄바꿈 문자 추가
        
//         byte[] data = Encoding.UTF8.GetBytes(message);

//         try
//         {
//             lock (stream)
//             {
//                 stream.Write(data, 0, data.Length);
//                 byte[] buffer = new byte[1024];
//                 int bytesRead = stream.Read(buffer, 0, buffer.Length);
//                 string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
//                 Debug.Log("Python Response: " + response);

//                 // Python 응답에 따라 CustomCapsuleHand의 에피소드 로직 호출
//                 if (response.Contains("OK") && !response.Contains("DISCARDED"))
//                 {
//                     RightHand.RecordTrialOutcome(error, true); // 유효한 시도
//                     Debug.Log("adaptive is working!@!");
//                 }
//                 else if (response.Contains("DISCARDED"))
//                 {
//                     RightHand.RecordTrialOutcome(error, false); // 폐기된 시도
//                 }
//             }
//         }
//         catch (SocketException e)
//         {
//             Debug.LogError("Socket error: " + e.Message);
//             isRunning = false;
//         }
//     }

//     void OnApplicationQuit()
//     {
//         isRunning = false;
//         sendThread?.Join();
//         stream?.Close();
//         client?.Close();
//     }
// }

// TCPClient.cs
// using UnityEngine;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;
// using System.Collections.Generic;

// public class TCPClient : MonoBehaviour
// {
//     [SerializeField]
//     public GameObject button; // CustomFeedbackProvider가 붙어있는 GameObject 참조

//     // 기존 트라이얼 데이터 전송을 위한 변수
//     private TcpClient trialClient; // 이름 변경
//     private NetworkStream trialStream; // 이름 변경
//     public string serverIP = "127.0.0.1";
//     public int trialServerPort = 25001; // 포트 번호 명시적으로 변경

//     // --- 실시간 상태 전송을 위한 새로운 변수 추가 ---
//     private TcpClient realTimeClient;
//     private NetworkStream realTimeStream;
//     public int realTimeServerPort = 25002; // 실시간 통신을 위한 새로운 포트
//     private Thread realTimeSendThread;
//     private bool realTimeIsRunning = false;
//     // ----------------------------------------------

//     public Leap.CustomCapsuleHand RightHand;
//     public CustomFeedbackProvider FeedbackProvider;

//     private Thread trialSendThread; // 이름 변경
//     private bool trialIsRunning = false; // 이름 변경

//     private bool sendingActive = false;

//     public int num_trial = 0;
//     // private Leap.CustomCapsuleHand.MotionState prevState = Leap.CustomCapsuleHand.MotionState.None; // 사용되지 않음

//     private List<float> indexZSequence = new List<float>();

//     // CustomFeedbackProvider에서 받을 실시간 상태 변수
//     public bool isVibrotactileConditionMet = false; // !RightHand.freezeConditionDetected && RightHand.IsCloseEnough 조건 충족 여부

//     void Start()
//     {
//         // --- 기존 트라이얼 데이터 클라이언트 초기화 ---
//         trialClient = new TcpClient();
//         trialClient.Connect(serverIP, trialServerPort);
//         trialStream = trialClient.GetStream();
//         trialIsRunning = true;
//         trialSendThread = new Thread(TrialSendLoop); // 스레드 이름 변경
//         trialSendThread.IsBackground = true;
//         trialSendThread.Start();
//         // ----------------------------------------------

//         // --- 실시간 데이터 클라이언트 초기화 ---
//         realTimeClient = new TcpClient();
//         realTimeClient.Connect(serverIP, realTimeServerPort);
//         realTimeStream = realTimeClient.GetStream();
//         realTimeIsRunning = true;
//         realTimeSendThread = new Thread(RealTimeSendLoop); // 새로운 스레드
//         realTimeSendThread.IsBackground = true;
//         realTimeSendThread.Start();
//         // ----------------------------------------------

//         FeedbackProvider = button.GetComponent<CustomFeedbackProvider>();
//         if (FeedbackProvider == null)
//         {
//             Debug.LogError("CustomFeedbackProvider not found on the assigned button GameObject.");
//         }
//     }

//     // CustomFeedbackProvider에서 호출될 메서드
//     public void SetVibrotactileCondition(bool conditionMet)
//     {
//         isVibrotactileConditionMet = conditionMet;
//     }

//     // --- 기존 트라이얼 데이터 전송 루프 (이름 변경) ---
//     void TrialSendLoop()
//     {
//         while (trialIsRunning)
//         {
//             if (RightHand == null || FeedbackProvider == null) continue;

//             var state = RightHand.currentState;
//             // Debug.LogFormat("Trial Sending active: {0}", state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive); // 너무 많은 로그 발생 가능성
//             if (state == Leap.CustomCapsuleHand.MotionState.Start && !sendingActive)
//             {
//                 sendingActive = true;
//                 indexZSequence.Clear();
//                 Debug.Log("Start detected - begin buffering for trial data.");
//             }

//             if (sendingActive)
//             {
//                 indexZSequence.Add(RightHand.index_position.z);

//                 if (state == Leap.CustomCapsuleHand.MotionState.End)
//                 {
//                     Debug.Log("End detected - stop buffering and send trial data.");
//                     sendingActive = false;
//                     num_trial += 1;
//                     SendTrialData();
//                 }
//             }

//             Thread.Sleep(10); // 10ms 간격으로 버퍼링
//         }
//     }
//     // --------------------------------------------------

//     // --- 실시간 상태 전송 루프 (새로 추가) ---
//     void RealTimeSendLoop()
//     {
//         while (realTimeIsRunning)
//         {
//             if (realTimeClient == null || !realTimeClient.Connected || realTimeStream == null)
//             {
//                 Thread.Sleep(100); // 연결될 때까지 잠시 대기
//                 continue;
//             }

//             // isVibrotactileConditionMet 상태를 문자열로 변환
//             string message = $"vibroCondition:{isVibrotactileConditionMet}\n";
//             byte[] data = Encoding.UTF8.GetBytes(message);

//             try
//             {
//                 lock (realTimeStream) // 실시간 스트림에 대한 락
//                 {
//                     realTimeStream.Write(data, 0, data.Length);
//                     // 실시간 응답은 받지 않거나, 매우 간단하게 처리 (예: "OK"만)
//                     // byte[] buffer = new byte[1024];
//                     // int bytesRead = realTimeStream.Read(buffer, 0, buffer.Length);
//                     // string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
//                     // Debug.Log("Python Real-time Response: " + response);
//                 }
//             }
//             catch (SocketException e)
//             {
//                 Debug.LogError("Real-time Socket error: " + e.Message);
//                 realTimeIsRunning = false;
//             }
//             catch (System.Exception e) // 다른 일반 예외 처리
//             {
//                 Debug.LogError("Real-time SendLoop unexpected error: " + e.Message);
//                 realTimeIsRunning = false;
//             }

//             Thread.Sleep(16); // 약 60 FPS (1000ms / 60 = 16.6ms)
//         }
//     }
//     // ------------------------------------------

//     // --- 기존 트라이얼 데이터 전송 메서드 ---
//     void SendTrialData()
//     {
//         float maxZ = RightHand.trialMaxIndexZList.Count > 0 ? 
//             RightHand.trialMaxIndexZList[RightHand.trialMaxIndexZList.Count - 1] : -999f;

//         float impact = RightHand.impact_position;
//         float error = maxZ - RightHand.GROUND_TRUTH;

//         string zSequenceStr = string.Join(",", indexZSequence);

//         string feedbackType = FeedbackProvider._feedbackPreset.ToString(); 
        
//         // 실시간 상태는 여기서 보내지 않음 (별도의 소켓으로 전송)
//         string message = $"trial:{num_trial}|indexZs:[{zSequenceStr}]|maxZ:{maxZ}|impact:{impact}|error:{error}|feedbackType:{feedbackType}\n"; 
        
//         byte[] data = Encoding.UTF8.GetBytes(message);

//         try
//         {
//             lock (trialStream) // 트라이얼 스트림에 대한 락
//             {
//                 trialStream.Write(data, 0, data.Length);
//                 byte[] buffer = new byte[1024];
//                 int bytesRead = trialStream.Read(buffer, 0, buffer.Length);
//                 string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
//                 Debug.Log("Python Trial Response: " + response);

//                 if (response.Contains("OK") && !response.Contains("DISCARDED"))
//                 {
//                     RightHand.RecordTrialOutcome(error, true);
//                     Debug.Log("Adaptive is working!@!");
//                 }
//                 else if (response.Contains("DISCARDED"))
//                 {
//                     RightHand.RecordTrialOutcome(error, false);
//                 }
//             }
//         }
//         catch (SocketException e)
//         {
//             Debug.LogError("Trial Socket error: " + e.Message);
//             trialIsRunning = false;
//         }
//         catch (System.Exception e) // 다른 일반 예외 처리
//         {
//             Debug.LogError("Trial SendData unexpected error: " + e.Message);
//             trialIsRunning = false;
//         }
//     }
//     // ----------------------------------------

//     void OnApplicationQuit()
//     {
//         // 모든 스레드 종료
//         trialIsRunning = false;
//         trialSendThread?.Join();
//         trialStream?.Close();
//         trialClient?.Close();

//         realTimeIsRunning = false;
//         realTimeSendThread?.Join();
//         realTimeStream?.Close();
//         realTimeClient?.Close();
//     }
// }

// TCPClient.cs (기존 TCPClient.cs 파일 내용)
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Generic;

public class TCPClient : MonoBehaviour
{
    [SerializeField]
    public GameObject button; // CustomFeedbackProvider가 붙어있는 GameObject 참조

    // 기존 트라이얼 데이터 전송을 위한 변수
    private TcpClient trialClient;
    private NetworkStream trialStream;
    public string serverIP = "127.0.0.1";
    public int trialServerPort = 25001; // 플로팅 스크립트의 포트와 일치

    // RealtimeTCPClient 참조 추가
    public RealtimeTCPClient RealtimeClientInstance; // Inspector에서 할당하거나 FindObjectOfType으로 찾습니다.

    public Leap.CustomCapsuleHand RightHand;
    public CustomFeedbackProvider FeedbackProvider;

    private Thread trialSendThread;
    private bool trialIsRunning = false;

    private bool sendingActive = false;

    public int num_trial = 0;

    private List<float> indexZSequence = new List<float>();

    // isVibrotactileConditionMet 변수는 RealtimeTCPClient로 이동했으므로 여기서는 제거합니다.
    // public bool isVibrotactileConditionMet = false; 

    void Start()
    {
        // --- 기존 트라이얼 데이터 클라이언트 초기화 ---
        trialClient = new TcpClient();
        try
        {
            trialClient.Connect(serverIP, trialServerPort);
            trialStream = trialClient.GetStream();
            trialIsRunning = true;
            trialSendThread = new Thread(TrialSendLoop);
            trialSendThread.IsBackground = true;
            trialSendThread.Start();
            Debug.Log($"TCPClient (Trial) connected to {serverIP}:{trialServerPort}");
        }
        catch (SocketException e)
        {
            Debug.LogError($"TCPClient (Trial) connection failed to port {trialServerPort}: {e.Message}. Make sure Python plotting server is running.");
            trialIsRunning = false;
        }
        // ----------------------------------------------

        // RealtimeTCPClient는 별도의 스크립트에서 초기화되므로 여기서는 제거합니다.
        // 이 스크립트에서 RealtimeTCPClient 인스턴스를 찾거나 Inspector에서 할당합니다.
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

    // 이 메서드는 CustomFeedbackProvider에서 RealtimeTCPClient 인스턴스로 직접 호출되므로 여기서는 필요 없습니다.
    // public void SetVibrotactileCondition(bool conditionMet)
    // {
    //     isVibrotactileConditionMet = conditionMet;
    // }

    void TrialSendLoop()
    {
        while (trialIsRunning)
        {
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
                    SendTrialData();
                }
            }

            Thread.Sleep(10);
        }
        Debug.Log("TCPClient (Trial) SendLoop finished.");
    }

    void SendTrialData()
    {
        if (trialClient == null || !trialClient.Connected || trialStream == null)
        {
            Debug.LogError("Trial client not connected. Cannot send trial data.");
            return;
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
            Debug.LogError("Trial Socket error: " + e.Message + ". Closing connection.");
            trialIsRunning = false;
        }
        catch (System.ObjectDisposedException)
        {
            Debug.LogWarning("Trial stream/client disposed during write.");
            trialIsRunning = false;
        }
        catch (System.Exception e)
        {
            Debug.LogError("Trial SendData unexpected error: " + e.Message + ". Stopping loop.");
            trialIsRunning = false;
        }
    }

    void OnApplicationQuit()
    {
        trialIsRunning = false;
        if (trialSendThread != null && trialSendThread.IsAlive) trialSendThread.Join();
        if (trialStream != null) trialStream.Close();
        if (trialClient != null) trialClient.Close();
        Debug.Log("TCPClient (Trial) connections closed.");

        // RealtimeTCPClient는 자체 OnApplicationQuit에서 종료를 처리하므로 여기서는 호출하지 않습니다.
    }
}