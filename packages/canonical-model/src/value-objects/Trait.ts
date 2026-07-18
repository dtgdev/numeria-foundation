export class Trait {
  public readonly name: string;
  public readonly description?: string;

  public constructor(name: string, description?: string) {
    const normalized = name.trim();

    if (!normalized) {
      throw new Error("Trait name is required.");
    }

    this.name = normalized;
    this.description = description?.trim();

    Object.freeze(this);
  }

  public equals(other: Trait): boolean {
    return this.name.toLowerCase() === other.name.toLowerCase();
  }

  public toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      description: this.description,
    };
  }
}
