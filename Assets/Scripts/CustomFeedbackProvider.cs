
using UnityEngine;
using System.Collections;
using Bhaptics.SDK2;
using Bhaptics.SDK2.Glove;

public class CustomFeedbackProvider : MonoBehaviour
{
    [SerializeField]
    public GameObject PressableObject;
    public GameObject pseudo_PressableObject;
    [SerializeField]
    public Leap.CustomCapsuleHand RightHand;

    // RealtimeTCPClient 스크립트 참조 추가
    public RealtimeTCPClient realtimeTcpClient; 

    private Leap.PhysicalHands.IgnorePhysicalHands _ignore;
    private Leap.Examples.SimpleInteractionGlow _buttonColor;

    private Rigidbody rigidBody_pressable;  

    public enum FeedbackType
    {
        OnlyVisual = 0,
        OnlyVibrotactile_fixed = 1,
        OnlyVibrotactile_adaptive = 2,
        VisualwithVibrotactile_fixed = 3,
        VisualwithVibrotactile_adaptive = 4
    }

    [SerializeField]
    public FeedbackType _feedbackPreset;

    private bool is_visual;
    private bool is_vibrotactile;
    public bool is_adaptive = false;

    public bool vibrotactile_applied = false;

    int[] contactMotorValueArray = new int[] { 0, 10, 0, 0, 0, 0 };
    int[] confirmMotorValueArray = new int[] { 0, 100, 0, 0, 0, 0 };

    public void UpdateFeedbackType()
    {
        switch (_feedbackPreset)
        {
            case FeedbackType.OnlyVisual:
                is_visual = true;
                is_vibrotactile = false;
                is_adaptive = false;
                break;
            case FeedbackType.OnlyVibrotactile_fixed:
                is_visual = false;
                is_vibrotactile = true;
                is_adaptive = false;
                break;
            case FeedbackType.OnlyVibrotactile_adaptive:
                is_visual = false;
                is_vibrotactile = true;
                is_adaptive = true;
                break;
            case FeedbackType.VisualwithVibrotactile_fixed:
                is_visual = true;
                is_vibrotactile = true;
                is_adaptive = false;
                break;
            case FeedbackType.VisualwithVibrotactile_adaptive:
                is_visual = true;
                is_vibrotactile = true;
                is_adaptive = true;
                break;
        }
        ActivateFeedbackType();
    }

    private void ActivateFeedbackType()
    {
        Renderer r = PressableObject.GetComponent<MeshRenderer>();
        Renderer pseudo_r = pseudo_PressableObject.GetComponent<MeshRenderer>();
        if (!is_visual)
        {
            r.enabled = false;
            pseudo_r.enabled = true;
            _buttonColor.isColorActive = false;
        }
        else
        {
            r.enabled = true;
            pseudo_r.enabled = false;
            _buttonColor.isColorActive = true;
        }
        RightHand.is_adaptive = this.is_adaptive;
    }

    void Start()
    {
        _ignore = PressableObject.GetComponent<Leap.PhysicalHands.IgnorePhysicalHands>();
        _buttonColor = PressableObject.GetComponent<Leap.Examples.SimpleInteractionGlow>();
        rigidBody_pressable = PressableObject.GetComponent<Rigidbody>();
        rigidBody_pressable.constraints = RigidbodyConstraints.FreezePositionX | RigidbodyConstraints.FreezePositionY;
        
        // RealtimeTCPClient 참조를 동적으로 가져옵니다.
        if (realtimeTcpClient == null)
        {
            realtimeTcpClient = FindObjectOfType<RealtimeTCPClient>();
            if (realtimeTcpClient == null)
            {
                Debug.LogError("RealtimeTCPClient instance not found in the scene! Please ensure it's attached to a GameObject.");
            }
        }
    }

    void Update()
    {
        UpdateFeedbackType();
        
        // !RightHand.freezeConditionDetected && RightHand.IsCloseEnough(RightHand.currentTravel, RightHand.impact_position) 조건
        bool isConditionMet = !RightHand.freezeConditionDetected && RightHand.IsCloseEnough(RightHand.currentTravel, RightHand.impact_position);
        
        // RealtimeTCPClient가 할당되어 있다면 조건을 큐에 추가
        if (realtimeTcpClient != null)
        {
            realtimeTcpClient.EnqueueVibroCondition(isConditionMet);
        }

        if (isConditionMet)
        {
            Debug.LogFormat("jump: {0}", isConditionMet);
            if (is_vibrotactile)
            {
                ApplyVibrotactileFeedback(confirmMotorValueArray);
                vibrotactile_applied = true;
            }
        }
    }

    void ApplyVibrotactileFeedback(int[] MotorValueArray)
    {
        if (RightHand.freezeConditionDetected)
        {
            Debug.LogError("Freeze Condition; True");
        }
        BhapticsLibrary.PlayMotors(
                    9,  // # of index finger motor 
                    MotorValueArray,
                    5
                );
        RightHand.freezeConditionDetected = true;
    }
}