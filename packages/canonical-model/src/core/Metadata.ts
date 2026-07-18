export type MetadataValue =
  | string
  | number
  | boolean
  | null
  | readonly string[];

export type MetadataRecord = Readonly<Record<string, MetadataValue>>;

export interface MetadataProps {
  createdAt?: Date;
  updatedAt?: Date;
  createdBy?: string;
  updatedBy?: string;
  source?: string;
  attributes?: MetadataRecord;
}

export class Metadata {
  public readonly createdAt: Date;
  public readonly updatedAt: Date;
  public readonly createdBy?: string;
  public readonly updatedBy?: string;
  public readonly source?: string;
  public readonly attributes: MetadataRecord;

  public constructor(props: MetadataProps = {}) {
    const now = new Date();

    this.createdAt = new Date(props.createdAt ?? now);
    this.updatedAt = new Date(props.updatedAt ?? now);
    this.createdBy = Metadata.normalizeOptionalText(props.createdBy);
    this.updatedBy = Metadata.normalizeOptionalText(props.updatedBy);
    this.source = Metadata.normalizeOptionalText(props.source);
    this.attributes = Object.freeze({
      ...(props.attributes ?? {}),
    });

    if (this.updatedAt.getTime() < this.createdAt.getTime()) {
      throw new Error("updatedAt cannot occur before createdAt.");
    }

    Object.freeze(this);
  }

  public withUpdate(
    updates: Omit<MetadataProps, "createdAt" | "createdBy"> = {},
  ): Metadata {
    return new Metadata({
      createdAt: this.createdAt,
      createdBy: this.createdBy,
      updatedAt: updates.updatedAt ?? new Date(),
      updatedBy: updates.updatedBy ?? this.updatedBy,
      source: updates.source ?? this.source,
      attributes: {
        ...this.attributes,
        ...(updates.attributes ?? {}),
      },
    });
  }

  public toJSON(): Record<string, unknown> {
    return {
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      createdBy: this.createdBy,
      updatedBy: this.updatedBy,
      source: this.source,
      attributes: this.attributes,
    };
  }

  private static normalizeOptionalText(value?: string): string | undefined {
    if (value === undefined) {
      return undefined;
    }

    const normalized = value.trim();
    return normalized.length > 0 ? normalized : undefined;
  }
}
