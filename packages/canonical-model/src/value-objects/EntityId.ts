export class EntityId {
  public readonly value: string;

  public constructor(value: string) {
    const normalized = value.trim().toLowerCase();

    if (
      !/^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$/.test(normalized)
    ) {
      throw new Error(
        `Invalid EntityId "${value}". Example: character.derivative`
      );
    }

    this.value = normalized;

    Object.freeze(this);
  }

  public equals(other: EntityId): boolean {
    return this.value === other.value;
  }

  public toString(): string {
    return this.value;
  }

  public toJSON(): string {
    return this.value;
  }
}
