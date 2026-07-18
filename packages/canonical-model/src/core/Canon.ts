import { CanonStatus } from "../enums/CanonStatus.js";

export interface CanonProps {
  status: CanonStatus;
  approvedBy?: string;
  approvedAt?: Date;
  notes?: string;
}

export class Canon {
  public readonly status: CanonStatus;
  public readonly approvedBy?: string;
  public readonly approvedAt?: Date;
  public readonly notes?: string;

  public constructor(props: CanonProps) {
    this.status = props.status;
    this.approvedBy = Canon.normalizeOptionalText(props.approvedBy);
    this.approvedAt = props.approvedAt
      ? new Date(props.approvedAt)
      : undefined;
    this.notes = Canon.normalizeOptionalText(props.notes);

    this.validate();

    Object.freeze(this);
  }

  public static draft(): Canon {
    return new Canon({
      status: CanonStatus.DRAFT,
    });
  }

  public approve(approvedBy: string, approvedAt = new Date()): Canon {
    const reviewer = approvedBy.trim();

    if (!reviewer) {
      throw new Error("approvedBy is required when approving canon.");
    }

    return new Canon({
      status: CanonStatus.APPROVED,
      approvedBy: reviewer,
      approvedAt,
      notes: this.notes,
    });
  }

  public makeCanonical(
    approvedBy: string,
    approvedAt = new Date(),
  ): Canon {
    const reviewer = approvedBy.trim();

    if (!reviewer) {
      throw new Error(
        "approvedBy is required when making an entity canonical.",
      );
    }

    return new Canon({
      status: CanonStatus.CANONICAL,
      approvedBy: reviewer,
      approvedAt,
      notes: this.notes,
    });
  }

  public archive(notes?: string): Canon {
    return new Canon({
      status: CanonStatus.ARCHIVED,
      approvedBy: this.approvedBy,
      approvedAt: this.approvedAt,
      notes: notes ?? this.notes,
    });
  }

  public isPublished(): boolean {
    return (
      this.status === CanonStatus.APPROVED ||
      this.status === CanonStatus.CANONICAL
    );
  }

  public toJSON(): Record<string, unknown> {
    return {
      status: this.status,
      approvedBy: this.approvedBy,
      approvedAt: this.approvedAt?.toISOString(),
      notes: this.notes,
    };
  }

  private validate(): void {
    const requiresApproval =
      this.status === CanonStatus.APPROVED ||
      this.status === CanonStatus.CANONICAL;

    if (requiresApproval && (!this.approvedBy || !this.approvedAt)) {
      throw new Error(
        `${this.status} canon requires approvedBy and approvedAt.`,
      );
    }
  }

  private static normalizeOptionalText(value?: string): string | undefined {
    if (value === undefined) {
      return undefined;
    }

    const normalized = value.trim();
    return normalized.length > 0 ? normalized : undefined;
  }
}
