// RealtimeTCPClient.cs
// using UnityEngine;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;

// public class RealtimeTCPClient : MonoBehaviour
// {
//     private TcpClient realTimeClient;
//     private NetworkStream realTimeStream;
//     public string serverIP = "127.0.0.1";
//     public int realTimeServerPort = 25002; // Python 게임의 포트와 일치

//     private Thread realTimeSendThread;
//     private bool realTimeIsRunning = false;

//     // CustomFeedbackProvider로부터 받을 실시간 상태 변수
//     public volatile bool isVibrotactileConditionMet = false; // !RightHand.freezeConditionDetected && RightHand.IsCloseEnough 조건 충족 여부

//     void Start()
//     {
//         // --- 실시간 데이터 클라이언트 초기화 ---
//         realTimeClient = new TcpClient();
//         try
//         {
//             realTimeClient.Connect(serverIP, realTimeServerPort);
//             realTimeStream = realTimeClient.GetStream();
//             realTimeIsRunning = true;
//             realTimeSendThread = new Thread(RealTimeSendLoop);
//             realTimeSendThread.IsBackground = true; // 백그라운드 스레드로 설정하여 애플리케이션 종료 시 함께 종료
//             realTimeSendThread.Start();
//             Debug.Log($"RealtimeTCPClient connected to {serverIP}:{realTimeServerPort}");
//         }
//         catch (SocketException e)
//         {
//             Debug.LogError($"RealtimeTCPClient connection failed to port {realTimeServerPort}: {e.Message}. Make sure Python game server is running.");
//             realTimeIsRunning = false; // 연결 실패 시 스레드 시작 안 함
//         }
//     }

//     // CustomFeedbackProvider에서 호출될 메서드
//     public void SetVibrotactileCondition(bool conditionMet)
//     {
//         isVibrotactileConditionMet = conditionMet;
//     }

//     // --- 실시간 상태 전송 루프 ---
//     void RealTimeSendLoop()
//     {
//         while (realTimeIsRunning)
//         {
//             if (realTimeClient == null || !realTimeClient.Connected || realTimeStream == null)
//             {
//                 // 연결이 끊어졌거나 초기화되지 않은 경우
//                 Debug.LogWarning("RealtimeTCPClient: Not connected or stream is null. Attempting to reconnect...");
//                 Thread.Sleep(1000); // 1초 후 재연결 시도
//                 try
//                 {
//                     realTimeClient = new TcpClient();
//                     realTimeClient.Connect(serverIP, realTimeServerPort);
//                     realTimeStream = realTimeClient.GetStream();
//                     Debug.Log($"RealtimeTCPClient reconnected to {serverIP}:{realTimeServerPort}");
//                 }
//                 catch (SocketException e)
//                 {
//                     Debug.LogError($"RealtimeTCPClient reconnection failed: {e.Message}");
//                     // 계속 재시도
//                 }
//                 continue; // 다음 루프에서 다시 연결 상태 확인
//             }

//             // isVibrotactileConditionMet 상태를 문자열로 변환
//             string message = $"vibroCondition:{isVibrotactileConditionMet}\n";
//             Debug.LogFormat("Realtime Client says: {0}",isVibrotactileConditionMet);
//             byte[] data = Encoding.UTF8.GetBytes(message);

//             try
//             {
//                 lock (realTimeStream) // 실시간 스트림에 대한 락
//                 {
//                     realTimeStream.Write(data, 0, data.Length);
//                 }
//             }
//             catch (SocketException e)
//             {
//                 Debug.LogError("RealtimeTCPClient Socket error: " + e.Message + ". Closing connection.");
//                 realTimeIsRunning = false; // 소켓 에러 발생 시 루프 종료
//             }
//             catch (System.ObjectDisposedException)
//             {
//                 Debug.LogWarning("RealtimeTCPClient stream/client disposed during write. Stopping loop.");
//                 realTimeIsRunning = false; // 객체가 이미 해제된 경우 루프 종료
//             }
//             catch (System.Exception e)
//             {
//                 Debug.LogError("RealtimeTCPClient SendLoop unexpected error: " + e.Message + ". Stopping loop.");
//                 realTimeIsRunning = false; // 그 외 일반 예외 발생 시 루프 종료
//             }

//             Thread.Sleep(16); // 약 60 FPS (1000ms / 60 = 16.6ms)
//         }
//         Debug.Log("RealtimeTCPClient SendLoop finished.");
//     }

//     void OnApplicationQuit()
//     {
//         realTimeIsRunning = false;
//         // 스레드가 정상적으로 종료될 때까지 기다림
//         if (realTimeSendThread != null && realTimeSendThread.IsAlive)
//         {
//             realTimeSendThread.Join();
//         }
//         // 스트림과 클라이언트 소켓 닫기
//         if (realTimeStream != null)
//         {
//             realTimeStream.Close();
//             realTimeStream = null; // null로 설정하여 중복 닫기 방지
//         }
//         if (realTimeClient != null)
//         {
//             realTimeClient.Close();
//             realTimeClient = null; // null로 설정하여 중복 닫기 방지
//         }
//         Debug.Log("RealtimeTCPClient connections closed.");
//     }
// }

// RealtimeTCPClient.cs
using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent; // ConcurrentQueue를 사용하기 위해 추가

public class RealtimeTCPClient : MonoBehaviour
{
    private TcpClient realTimeClient;
    private NetworkStream realTimeStream;
    public string serverIP = "127.0.0.1";
    public int realTimeServerPort = 25002; // Python 게임의 포트와 일치

    private Thread realTimeSendThread;
    private bool realTimeIsRunning = false;

    // CustomFeedbackProvider로부터 받을 실시간 상태 변수 (이 변수는 큐를 통해 업데이트될 것입니다.)
    // 이제 이 변수는 주로 RealTimeSendLoop 내부에서 마지막으로 전송된 상태를 추적하는 데 사용됩니다.
    // public bool isVibrotactileConditionMet = false; // 이제 필요 없거나 큐에서 값을 받아 업데이트

    // 메시지를 위한 스레드 안전한 큐
    private ConcurrentQueue<bool> vibroConditionQueue = new ConcurrentQueue<bool>();
    private bool lastSentVibroCondition = false; // 중복 메시지 전송 방지


    void Start()
    {
        // --- 실시간 데이터 클라이언트 초기화 ---
        realTimeClient = new TcpClient();
        try
        {
            realTimeClient.Connect(serverIP, realTimeServerPort);
            realTimeStream = realTimeClient.GetStream();
            realTimeIsRunning = true;
            realTimeSendThread = new Thread(RealTimeSendLoop);
            realTimeSendThread.IsBackground = true; // 백그라운드 스레드로 설정하여 애플리케이션 종료 시 함께 종료
            realTimeSendThread.Start();
            Debug.Log($"RealtimeTCPClient connected to {serverIP}:{realTimeServerPort}");
        }
        catch (SocketException e)
        {
            Debug.LogError($"RealtimeTCPClient connection failed to port {realTimeServerPort}: {e.Message}. Make sure Python game server is running.");
            realTimeIsRunning = false; // 연결 실패 시 스레드 시작 안 함
        }
    }

    // CustomFeedbackProvider에서 호출될 메서드: 조건을 큐에 추가
    public void EnqueueVibroCondition(bool condition)
    {
        // 조건이 변경된 경우에만 큐에 넣어서 메시지 스팸 방지
        if (condition != lastSentVibroCondition)
        {
            vibroConditionQueue.Enqueue(condition);
        }
    }

    // --- 실시간 상태 전송 루프 ---
    void RealTimeSendLoop()
    {
        while (realTimeIsRunning)
        {
            if (realTimeClient == null || !realTimeClient.Connected || realTimeStream == null)
            {
                // 연결이 끊어졌거나 초기화되지 않은 경우
                Debug.LogWarning("RealtimeTCPClient: Not connected or stream is null. Attempting to reconnect...");
                Thread.Sleep(1000); // 1초 후 재연결 시도
                try
                {
                    realTimeClient = new TcpClient();
                    realTimeClient.Connect(serverIP, realTimeServerPort);
                    realTimeStream = realTimeClient.GetStream();
                    Debug.Log($"RealtimeTCPClient reconnected to {serverIP}:{realTimeServerPort}");
                }
                catch (SocketException e)
                {
                    Debug.LogError($"RealtimeTCPClient reconnection failed: {e.Message}");
                    // 계속 재시도
                }
                continue; // 다음 루프에서 다시 연결 상태 확인
            }

            bool conditionToSend = lastSentVibroCondition; // 기본적으로 마지막으로 전송된 상태로 설정

            // 큐에서 새 조건이 있는지 확인
            if (vibroConditionQueue.TryDequeue(out bool newCondition))
            {
                conditionToSend = newCondition;
                lastSentVibroCondition = newCondition; // 마지막으로 전송된 조건 업데이트
            }

            // isVibrotactileConditionMet 상태를 문자열로 변환
            string message = $"vibroCondition:{conditionToSend}\n";
            Debug.LogFormat("Realtime Client says: {0}", conditionToSend);
            byte[] data = Encoding.UTF8.GetBytes(message);

            try
            {
                lock (realTimeStream) // 실시간 스트림에 대한 락
                {
                    realTimeStream.Write(data, 0, data.Length);
                }
            }
            catch (SocketException e)
            {
                Debug.LogError("RealtimeTCPClient Socket error: " + e.Message + ". Closing connection.");
                realTimeIsRunning = false; // 소켓 에러 발생 시 루프 종료
            }
            catch (System.ObjectDisposedException)
            {
                Debug.LogWarning("RealtimeTCPClient stream/client disposed during write. Stopping loop.");
                realTimeIsRunning = false; // 객체가 이미 해제된 경우 루프 종료
            }
            catch (System.Exception e)
            {
                Debug.LogError("RealtimeTCPClient SendLoop unexpected error: " + e.Message + ". Stopping loop.");
                realTimeIsRunning = false; // 그 외 일반 예외 발생 시 루프 종료
            }

            Thread.Sleep(16); // 약 60 FPS (1000ms / 60 = 16.6ms)
        }
        Debug.Log("RealtimeTCPClient SendLoop finished.");
    }

    void OnApplicationQuit()
    {
        realTimeIsRunning = false;
        // 스레드가 정상적으로 종료될 때까지 기다림
        if (realTimeSendThread != null && realTimeSendThread.IsAlive)
        {
            realTimeSendThread.Join();
        }
        // 스트림과 클라이언트 소켓 닫기
        if (realTimeStream != null)
        {
            realTimeStream.Close();
            realTimeStream = null; // null로 설정하여 중복 닫기 방지
        }
        if (realTimeClient != null)
        {
            realTimeClient.Close();
            realTimeClient = null; // null로 설정하여 중복 닫기 방지
        }
        Debug.Log("RealtimeTCPClient connections closed.");
    }
}