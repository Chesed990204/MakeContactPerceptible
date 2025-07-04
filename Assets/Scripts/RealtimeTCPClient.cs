// // RealtimeTCPClient.cs
// using UnityEngine;
// using System.Net.Sockets;
// using System.Text;
// using System.Threading;
// using System.Collections.Concurrent; // ConcurrentQueue를 사용하기 위해 추가

// public class RealtimeTCPClient : MonoBehaviour
// {
//     private TcpClient realTimeClient;
//     private NetworkStream realTimeStream;
//     public string serverIP = "127.0.0.1";
//     public int realTimeServerPort = 25002; // Python 게임의 포트와 일치

//     private Thread realTimeSendThread;
//     private bool realTimeIsRunning = false;

//     // CustomFeedbackProvider로부터 받을 실시간 상태 변수 (이 변수는 큐를 통해 업데이트될 것입니다.)
//     // 이제 이 변수는 주로 RealTimeSendLoop 내부에서 마지막으로 전송된 상태를 추적하는 데 사용됩니다.
//     // public bool isVibrotactileConditionMet = false; // 이제 필요 없거나 큐에서 값을 받아 업데이트

//     // 메시지를 위한 스레드 안전한 큐
//     private ConcurrentQueue<bool> vibroConditionQueue = new ConcurrentQueue<bool>();
//     private bool lastSentVibroCondition = false; // 중복 메시지 전송 방지


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

//     // CustomFeedbackProvider에서 호출될 메서드: 조건을 큐에 추가
//     public void EnqueueVibroCondition(bool condition)
//     {
//         // 조건이 변경된 경우에만 큐에 넣어서 메시지 스팸 방지
//         if (condition != lastSentVibroCondition)
//         {
//             vibroConditionQueue.Enqueue(condition);
//         }
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

//             bool conditionToSend = lastSentVibroCondition; // 기본적으로 마지막으로 전송된 상태로 설정

//             // 큐에서 새 조건이 있는지 확인
//             if (vibroConditionQueue.TryDequeue(out bool newCondition))
//             {
//                 conditionToSend = newCondition;
//                 lastSentVibroCondition = newCondition; // 마지막으로 전송된 조건 업데이트
//             }

//             // isVibrotactileConditionMet 상태를 문자열로 변환
//             string message = $"vibroCondition:{conditionToSend}\n";
//             Debug.LogFormat("Realtime Client says: {0}", conditionToSend);
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

    // 메시지를 위한 스레드 안전한 큐
    private ConcurrentQueue<bool> vibroConditionQueue = new ConcurrentQueue<bool>();
    private bool lastSentVibroCondition = false; // 중복 메시지 전송 방지

    // NEW: True 신호를 최소한으로 유지하기 위한 변수들
    [Tooltip("True 신호가 최소한으로 유지될 시간 (초)")]
    public float minTrueDuration = 0.05f; // 예: 50ms (Python의 30FPS는 약 33.3ms/프레임이므로, 최소 50ms는 유지)
    private float trueConditionStartTime = -1f; // True 상태가 된 시각 (Time.time)
    private bool pendingTrueCondition = false; // CustomFeedbackProvider로부터 True를 받았음을 표시 (아직 minTrueDuration이 안 지난 경우)


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
        // Debug.Log($"[RealtimeTCPClient] EnqueueVibroCondition called with: {condition}"); // 디버그 추가

        if (condition) // True 신호가 들어왔을 때
        {
            // True 신호가 들어오면, 최소 유지 시간을 시작
            pendingTrueCondition = true;
            trueConditionStartTime = Time.time;
            // 즉시 True를 큐에 넣어서 보낼 수 있도록 함 (이전 lastSentVibroCondition과 다를 경우)
            if (!lastSentVibroCondition) // 이전에 False였을 때만 True를 큐에 추가하여 즉시 보내게 함
            {
                vibroConditionQueue.Enqueue(true);
            }
            lastSentVibroCondition = true; // True 상태로 업데이트 (전송 스레드에서 참조할 수 있도록)
        }
        else // False 신호가 들어왔을 때
        {
            // True 신호가 최소 유지 시간 내에 있다면 False로 즉시 전환하지 않음
            if (pendingTrueCondition && Time.time - trueConditionStartTime < minTrueDuration)
            {
                // 아직 최소 유지 시간이 지나지 않았으므로, False 신호는 무시하고 True 상태 유지
                // Debug.Log($"[RealtimeTCPClient] False ignored. True still active for {minTrueDuration - (Time.time - trueConditionStartTime):.3f}s.");
            }
            else // 최소 유지 시간이 지났거나, 애초에 True 상태가 아니었다면 False로 전환 허용
            {
                if (lastSentVibroCondition) // 이전에 True였을 때만 False를 큐에 추가하여 보내게 함
                {
                    vibroConditionQueue.Enqueue(false);
                }
                lastSentVibroCondition = false;
                pendingTrueCondition = false; // False로 전환되었으므로 대기 중인 True 없음
            }
        }
    }

    // --- 실시간 상태 전송 루프 ---
    void RealTimeSendLoop()
    {
        while (realTimeIsRunning)
        {
            if (realTimeClient == null || !realTimeClient.Connected || realTimeStream == null)
            {
                Debug.LogWarning("RealtimeTCPClient: Not connected or stream is null. Attempting to reconnect...");
                Thread.Sleep(1000); 
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
                }
                continue; 
            }

            // 스레드 안전하게 큐에서 새 조건 가져오기
            bool conditionToSend;
            if (!vibroConditionQueue.IsEmpty) // 큐에 메시지가 있다면
            {
                if (vibroConditionQueue.TryDequeue(out bool newCondition))
                {
                    conditionToSend = newCondition;
                    // lastSentVibroCondition은 이미 EnqueueVibroCondition에서 업데이트됨.
                    // 여기서 다시 업데이트할 필요는 없지만, 일관성을 위해 유지할 수도 있음.
                    // lastSentVibroCondition = newCondition; // 주석 처리 또는 제거 가능
                }
                else
                {
                    conditionToSend = lastSentVibroCondition; // Dequeue 실패 시 마지막 값 사용
                }
            }
            else
            {
                conditionToSend = lastSentVibroCondition; // 큐가 비어있으면 마지막 상태 유지
            }

            // 메시지 전송 (현재 상태가 변경되지 않았어도 일정 주기로 전송)
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
                Debug.LogError("RealtimeTCPClient Socket error: " + e.Message + ". Closing connection.");
                realTimeIsRunning = false; 
            }
            catch (System.ObjectDisposedException)
            {
                Debug.LogWarning("RealtimeTCPClient stream/client disposed during write. Stopping loop.");
                realTimeIsRunning = false; 
            }
            catch (System.Exception e)
            {
                Debug.LogError("RealtimeTCPClient SendLoop unexpected error: " + e.Message + ". Stopping loop.");
                realTimeIsRunning = false; 
            }

            Thread.Sleep(16); // 약 60 FPS (1000ms / 60 = 16.6ms)
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