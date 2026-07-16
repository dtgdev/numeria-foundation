import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  PropsWithChildren,
} from "react";

import {
  getEntities,
  getEntityNeighbors,
  getSummary,
} from "../api";

import type {
  CanonEntity,
  CanonSummary,
  EntityNeighbors,
} from "../api";

import type {
  StudioSection,
} from "../components/layout";

interface StudioContextValue {
  activeSection: StudioSection;
  setActiveSection: (
    section: StudioSection,
  ) => void;

  summary: CanonSummary | null;
  entities: CanonEntity[];

  selectedId: string | null;
  selectedEntity: CanonEntity | null;
  selectEntity: (
    entityId: string | null,
  ) => void;

  selectedType: string;
  setSelectedType: (
    entityType: string,
  ) => void;

  query: string;
  setQuery: (
    query: string,
  ) => void;

  entityTypes: string[];
  filteredEntities: CanonEntity[];

  characters: CanonEntity[];
  worlds: CanonEntity[];
  regions: CanonEntity[];

  neighborData: EntityNeighbors | null;
  neighborsLoading: boolean;
  neighborsError: string;

  loading: boolean;
  error: string;

  loadStudio: () => Promise<void>;
  refreshStudio: (
    preferredEntityId?: string,
  ) => Promise<void>;
  refreshNeighbors: (
    entityId?: string,
  ) => Promise<void>;
}

const StudioContext =
  createContext<StudioContextValue | null>(
    null,
  );

export function StudioProvider({
  children,
}: PropsWithChildren) {
  const [
    activeSection,
    setActiveSection,
  ] = useState<StudioSection>("canon");

  const [summary, setSummary] =
    useState<CanonSummary | null>(null);

  const [entities, setEntities] =
    useState<CanonEntity[]>([]);

  const [selectedId, setSelectedId] =
    useState<string | null>(null);

  const [selectedType, setSelectedType] =
    useState("All");

  const [query, setQuery] = useState("");

  const [neighborData, setNeighborData] =
    useState<EntityNeighbors | null>(null);

  const [
    neighborsLoading,
    setNeighborsLoading,
  ] = useState(false);

  const [
    neighborsError,
    setNeighborsError,
  ] = useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const selectedEntity = useMemo(
    () =>
      entities.find(
        (entity) =>
          entity.id === selectedId,
      ) ?? null,
    [
      entities,
      selectedId,
    ],
  );

  const entityTypes = useMemo(
    () => [
      "All",
      ...Array.from(
        new Set(
          entities.map(
            (entity) => entity.type,
          ),
        ),
      ).sort(),
    ],
    [entities],
  );

  const filteredEntities = useMemo(
    () => {
      const normalizedQuery =
        query.trim().toLowerCase();

      return entities.filter(
        (entity) => {
          const matchesType =
            selectedType === "All" ||
            entity.type ===
              selectedType;

          const matchesQuery =
            normalizedQuery.length === 0 ||
            entity.name
              .toLowerCase()
              .includes(
                normalizedQuery,
              ) ||
            entity.id
              .toLowerCase()
              .includes(
                normalizedQuery,
              );

          return (
            matchesType &&
            matchesQuery
          );
        },
      );
    },
    [
      entities,
      query,
      selectedType,
    ],
  );

  const characters = useMemo(
    () =>
      entities.filter(
        (entity) =>
          entity.type === "Character",
      ),
    [entities],
  );

  const worlds = useMemo(
    () =>
      entities.filter(
        (entity) =>
          entity.type === "World",
      ),
    [entities],
  );

  const regions = useMemo(
    () =>
      entities.filter(
        (entity) =>
          entity.type === "Region",
      ),
    [entities],
  );

  const refreshNeighbors =
    useCallback(
      async (
        entityId?: string,
      ) => {
        const targetId =
          entityId ?? selectedId;

        if (!targetId) {
          setNeighborData(null);
          setNeighborsError("");
          return;
        }

        setNeighborsLoading(true);
        setNeighborsError("");

        try {
          const result =
            await getEntityNeighbors(
              targetId,
            );

          setNeighborData(result);
        } catch (caughtError) {
          setNeighborData(null);

          setNeighborsError(
            caughtError instanceof Error
              ? caughtError.message
              : "Failed to load relationships.",
          );
        } finally {
          setNeighborsLoading(false);
        }
      },
      [selectedId],
    );

  const loadStudio =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const [
          summaryData,
          entityData,
        ] = await Promise.all([
          getSummary(),
          getEntities(),
        ]);

        setSummary(summaryData);
        setEntities(entityData);

        setSelectedId(
          (currentId) => {
            if (
              currentId &&
              entityData.some(
                (entity) =>
                  entity.id ===
                  currentId,
              )
            ) {
              return currentId;
            }

            return (
              entityData[0]?.id ??
              null
            );
          },
        );
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Failed to load the Numeria canon.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  const refreshStudio =
    useCallback(
      async (
        preferredEntityId?: string,
      ) => {
        const [
          summaryData,
          entityData,
        ] = await Promise.all([
          getSummary(),
          getEntities(),
        ]);

        setSummary(summaryData);
        setEntities(entityData);

        let nextSelectedId =
          preferredEntityId ??
          selectedId;

        if (
          nextSelectedId &&
          !entityData.some(
            (entity) =>
              entity.id ===
              nextSelectedId,
          )
        ) {
          nextSelectedId =
            entityData[0]?.id ??
            null;
        }

        setSelectedId(
          nextSelectedId,
        );

        if (nextSelectedId) {
          await refreshNeighbors(
            nextSelectedId,
          );
        } else {
          setNeighborData(null);
        }
      },
      [
        refreshNeighbors,
        selectedId,
      ],
    );

  const selectEntity =
    useCallback(
      (
        entityId: string | null,
      ) => {
        setSelectedId(entityId);
      },
      [],
    );

  useEffect(() => {
    void loadStudio();
  }, [loadStudio]);

  useEffect(() => {
    if (!selectedId) {
      setNeighborData(null);
      return;
    }

    void refreshNeighbors(
      selectedId,
    );
  }, [
    refreshNeighbors,
    selectedId,
  ]);

  const value = useMemo<
    StudioContextValue
  >(
    () => ({
      activeSection,
      setActiveSection,

      summary,
      entities,

      selectedId,
      selectedEntity,
      selectEntity,

      selectedType,
      setSelectedType,

      query,
      setQuery,

      entityTypes,
      filteredEntities,

      characters,
      worlds,
      regions,

      neighborData,
      neighborsLoading,
      neighborsError,

      loading,
      error,

      loadStudio,
      refreshStudio,
      refreshNeighbors,
    }),
    [
      activeSection,
      summary,
      entities,
      selectedId,
      selectedEntity,
      selectEntity,
      selectedType,
      query,
      entityTypes,
      filteredEntities,
      characters,
      worlds,
      regions,
      neighborData,
      neighborsLoading,
      neighborsError,
      loading,
      error,
      loadStudio,
      refreshStudio,
      refreshNeighbors,
    ],
  );

  return (
    <StudioContext.Provider
      value={value}
    >
      {children}
    </StudioContext.Provider>
  );
}

export { StudioContext };
