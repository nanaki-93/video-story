/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Interpolation = "constant" | "linear";
/**
 * @minItems 1
 */
export type Keys = [CurveKey, ...CurveKey[]];
export type Frame = number;
export type Value = number;
export type Maximum = number;
export type Minimum = number;
export type Outside = "clamp" | "zero";
export type Scope = string;
export type Target = string;
export type Unit = "design_px_per_second" | "fraction" | "degrees" | "design_px" | "db";

export interface Curve {
  interpolation: Interpolation;
  keys: Keys;
  limits: ParameterLimit;
  outside?: Outside;
  scope: Scope;
  target: Target;
  unit: Unit;
}
/**
 * This interface was referenced by `Curve`'s JSON-Schema
 * via the `definition` "CurveKey".
 */
export interface CurveKey {
  frame: Frame;
  value: Value;
}
/**
 * This interface was referenced by `Curve`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
