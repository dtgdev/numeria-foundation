export interface VersionProps {
  major: number;
  minor: number;
  patch: number;
}

export class Version {
  public readonly major: number;
  public readonly minor: number;
  public readonly patch: number;

  public constructor(props: VersionProps) {
    Version.validatePart("major", props.major);
    Version.validatePart("minor", props.minor);
    Version.validatePart("patch", props.patch);

    this.major = props.major;
    this.minor = props.minor;
    this.patch = props.patch;

    Object.freeze(this);
  }

  public static initial(): Version {
    return new Version({
      major: 1,
      minor: 0,
      patch: 0,
    });
  }

  public static parse(value: string): Version {
    const match = /^(\d+)\.(\d+)\.(\d+)$/.exec(value);

    if (!match) {
      throw new Error(
        `Invalid version "${value}". Expected semantic version format such as 1.0.0.`,
      );
    }

    return new Version({
      major: Number(match[1]),
      minor: Number(match[2]),
      patch: Number(match[3]),
    });
  }

  public incrementMajor(): Version {
    return new Version({
      major: this.major + 1,
      minor: 0,
      patch: 0,
    });
  }

  public incrementMinor(): Version {
    return new Version({
      major: this.major,
      minor: this.minor + 1,
      patch: 0,
    });
  }

  public incrementPatch(): Version {
    return new Version({
      major: this.major,
      minor: this.minor,
      patch: this.patch + 1,
    });
  }

  public equals(other: Version): boolean {
    return (
      this.major === other.major &&
      this.minor === other.minor &&
      this.patch === other.patch
    );
  }

  public toString(): string {
    return `${this.major}.${this.minor}.${this.patch}`;
  }

  public toJSON(): VersionProps {
    return {
      major: this.major,
      minor: this.minor,
      patch: this.patch,
    };
  }

  private static validatePart(name: string, value: number): void {
    if (!Number.isInteger(value) || value < 0) {
      throw new Error(`${name} must be a non-negative integer.`);
    }
  }
}
