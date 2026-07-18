import { Entity } from "../core/Entity.js";
import type { EntityProps } from "../core/Entity.js";
import { EntityType } from "../enums/EntityType.js";

export interface CharacterProps extends Omit<EntityProps, "type"> {
  mathematicalConcept: string;
  symbol: string;
  personalityTraits: readonly string[];
  abilities: readonly string[];
  weaknesses: readonly string[];
  catchPhrase?: string;
}

export class Character extends Entity {
  public readonly mathematicalConcept: string;
  public readonly symbol: string;
  public readonly personalityTraits: readonly string[];
  public readonly abilities: readonly string[];
  public readonly weaknesses: readonly string[];
  public readonly catchPhrase?: string;

  public constructor(props: CharacterProps) {
    super({
      ...props,
      type: EntityType.CHARACTER,
    });

    this.mathematicalConcept = props.mathematicalConcept.trim();
    this.symbol = props.symbol.trim();
    this.personalityTraits = Object.freeze([...props.personalityTraits]);
    this.abilities = Object.freeze([...props.abilities]);
    this.weaknesses = Object.freeze([...props.weaknesses]);
    this.catchPhrase = props.catchPhrase?.trim();

    Object.freeze(this);
  }

  public override toJSON(): Record<string, unknown> {
    return {
      ...this.baseJSON(),
      mathematicalConcept: this.mathematicalConcept,
      symbol: this.symbol,
      personalityTraits: this.personalityTraits,
      abilities: this.abilities,
      weaknesses: this.weaknesses,
      catchPhrase: this.catchPhrase,
    };
  }
}
