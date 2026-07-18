export class Ability {
  public readonly name: string;
  public readonly description?: string;

  public constructor(name: string, description?: string) {
    const normalized = name.trim();

    if (!normalized) {
      throw new Error("Ability name is required.");
    }

    this.name = normalized;
    this.description = description?.trim();

    Object.freeze(this);
  }

  public toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      description: this.description,
    };
  }
}
