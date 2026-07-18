export class Tag {
  public readonly value: string;

  public constructor(value: string) {
    const normalized = Tag.normalize(value);

    if (normalized.length < 2) {
      throw new Error("A tag must contain at least two characters.");
    }

    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(normalized)) {
      throw new Error(
        `Invalid tag "${value}". Tags must use lowercase kebab-case.`,
      );
    }

    this.value = normalized;

    Object.freeze(this);
  }

  public equals(other: Tag): boolean {
    return this.value === other.value;
  }

  public toString(): string {
    return this.value;
  }

  public toJSON(): string {
    return this.value;
  }

  private static normalize(value: string): string {
    return value.trim().toLowerCase().replace(/\s+/g, "-");
  }
}
