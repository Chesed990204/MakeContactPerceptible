// using System.Collections;
// using System.Collections.Generic;
// using UnityEngine;
// using Leap.Unity;

// public class GetHandPosition : MonoBehaviour
// {
//     //public GameObject LeftScript;
//     public GameObject RightScript;
//     //public GameObject LCube, RCube;
//     // Start is called before the first frame update
//     void Start()
//     {
//         hand_model = GetComponent<GameObject>();
//     }

//     // Update is called once per frame
//     void Update()
//     {
//         Vector3 position = RightScript.GetComponent<Leap.Unity.CapsuleHand>()._spherePositions[0];
//         Debug.Log(position);   
//     }
// }

// // using UnityEngine;
// // using System.Collections;
// // using Leap;

// // public class GetHandPosition : MonoBehaviour 
// // {
// // 	public HandModel hand_model;
// // 	Hand leap_hand;

// // 	void Start() 
// // 	{
// // 		hand_model = GetComponent<HandModel>();
// // 		leap_hand = hand_model.GetLeapHand();
// // 		if (leap_hand == null) Debug.LogError("No leap_hand founded");
// // 	}

// // 	void Update() 
// // 	{
// // 		for (int i = 0; i < HandModel.NUM_FINGERS;i++)
// // 		{
// // 			FingerModel finger = hand_model.fingers[i];
// // 			// draw ray from finger tips (enable Gizmos in Game window to see)
// // 			Debug.DrawRay(finger.GetTipPosition(), finger.GetRay().direction, Color.red); 
// // 		}
// // 	}
// // }