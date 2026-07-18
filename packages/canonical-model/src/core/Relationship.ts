import { RelationshipType } from "../enums/RelationshipType.js";
import { EntityId } from "../value-objects/EntityId.js";
import { Metadata } from "./Metadata.js";

export interface RelationshipProps {
  id: string;
  type: RelationshipType;
  source: EntityId;
  target: EntityId;
  metadata?: Metadata;
  description?: string;
}

export class Relationship {
  public readonly id: string;
  public readonly type: RelationshipType;
  public readonly source: EntityId;
  public readonly target: EntityId;
  public readonly metadata: Metadata;
  public readonly description?: string;

  public constructor(props: RelationshipProps) {
    const normalizedId = props.id.trim();

    if (!normalizedId) {
      throw new Error("Relationship id is required.");
    }

    if (props.source.equals(props.target)) {
      throw new Error(
        "Relationship source and target cannot be the same entity."
      );
    }

    this.id = normalizedId;
    this.type = props.type;
    this.source = props.source;
    this.target = props.target;
    this.metadata = props.metadata ?? new Metadata();
    this.description = props.description?.trim();

    Object.freeze(this);
  }

  public toJSON(): Record<string, unknown> {
    return {
      id: this.id,
      type: this.type,
      source: this.source.toString(),
      target: this.target.toString(),
      description: this.description,
      metadata: this.metadata.toJSON(),
    };
  }
}
