// Test-only compile dependencies for TeaProgress. No world/presentation acceptance.
using System;
namespace Paridhwani {
 public enum VillageActivity {None}
 public enum StoryEnding {None,Stay,Depart}
 public enum VillageQuality {Balanced,Low,High}
 public static class CheckpostInvestigation {public static bool IsCheckpostPosition(UnityEngine.Vector3 p)=>false;}
 public static class RiverInvestigation {public static bool CanDeduce(TeaProgress p)=>false;}
 public static class PresentationPolicy {
  public const float DefaultBrightness=.7f;
  public static float Volume(float v)=>!float.IsFinite(v)?1:Math.Min(1,Math.Max(0,v));
  public static float Brightness(float v)=>!float.IsFinite(v)?DefaultBrightness:Math.Min(1.5f,Math.Max(-.5f,v));
  public static VillageQuality ValidQuality(VillageQuality q)=>q==VillageQuality.Low||q==VillageQuality.High?q:VillageQuality.Balanced;
 }
}
