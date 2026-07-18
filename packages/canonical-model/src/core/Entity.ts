import { EntityType } from "../enums/EntityType.js";
import { Canon } from "./Canon.js";
import { Metadata } from "./Metadata.js";
import { Tag } from "./Tag.js";
import { Version } from "./Version.js";

export interface EntityProps {
  id: string;
  type: EntityType;
  name: string;
  description: string;
  educationalPurpose: string;
  version?: Version;
  canon?: Canon;
  metadata?: Metadata;
  tags?: readonly Tag[];
}

export abstract class Entity {
  public readonly id: string;
  public readonly type: EntityType;
  public readonly name: string;
  public readonly description: string;
  public readonly educationalPurpose: string;
  public readonly version: Version;
  public readonly canon: Canon;
  public readonly metadata: Metadata;
  public readonly tags: readonly Tag[];

  protected constructor(props: EntityProps) {
    this.id = Entity.validateId(props.id);
    this.type = props.type;
    this.name = Entity.requireText("name", props.name);
    this.description = Entity.requireText(
      "description",
      props.description,
    );
    this.educationalPurpose = Entity.requireText(
      "educationalPurpose",
      props.educationalPurpose,
    );
    this.version = props.version ?? Version.initial();
    this.canon = props.canon ?? Canon.draft();
    this.metadata = props.metadata ?? new Metadata();
    this.tags = Object.freeze(Entity.uniqueTags(props.tags ?? []));

    Object.freeze(this.tags);
  }

  public hasTag(value: string): boolean {
    const normalized = new Tag(value);

    return this.tags.some((tag) => tag.equals(normalized));
  }

  public isCanonical(): boolean {
    return this.canon.status === "canonical";
  }

  public abstract toJSON(): Record<string, unknown>;

  protected baseJSON(): Record<string, unknown> {
    return {
      id: this.id,
      type: this.type,
      name: this.name,
      description: this.description,
      educationalPurpose: this.educationalPurpose,
      version: this.version.toString(),
      canon: this.canon.toJSON(),
      metadata: this.metadata.toJSON(),
      tags: this.tags.map((tag) => tag.toString()),
    };
  }

  private static validateId(value: string): string {
    const normalized = value.trim().toLowerCase();

    if (
      !/^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$/.test(normalized)
    ) {
      throw new Error(
        `Invalid entity id "${value}". Use a readable identifier such as character.derivative.`,
      );
    }

    return normalized;
  }

  private static requireText(name: string, value: string): string {
    const normalized = value.trim();

    if (!normalized) {
      throw new Error(`${name} is required.`);
    }

    return normalized;
  }

  private static uniqueTags(tags: readonly Tag[]): Tag[] {
    const unique = new Map<string, Tag>();

    for (const tag of tags) {
      unique.set(tag.value, tag);
    }

    return [...unique.values()];
  }
}
