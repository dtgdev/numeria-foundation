import {
  useEffect,
  useMemo,
  useState,
} from "react";

import type { CanonEntity } from "../../api";

import { Numeria } from "../../engine";

import type {
  StoryAnalysis,
} from "../../engine";

import {
  Badge,
  Button,
  Card,
} from "../../components/ui";

import { useStudio } from "../../hooks";

import {
  EntityLibrary,
  ForgeLayout,
  ForgeToolbar,
  SearchBar,
} from "../../shared";

import DirectorPanel from
  "../../intelligence/DirectorPanel/DirectorPanel";

import "./StoryStudio.css";

interface StoryStudioProps {
  onCreateStory?: () => void;
}

function readText(
  entity: CanonEntity,
  key: string,
  fallback: string,
): string {
  const value = entity.data[key];

  return typeof value === "string" && value.trim()
    ? value.trim()
    : fallback;
}

export default function StoryStudio({
  onCreateStory,
}: StoryStudioProps) {
  const {
    selectedEntity,
    selectedId,
    selectEntity,
  } = useStudio();

  const [query, setQuery] = useState("");

  const [analysis, setAnalysis] =
    useState<StoryAnalysis | null>(null);

  const [
    analysisLoading,
    setAnalysisLoading,
  ] = useState(false);

  const [
    analysisError,
    setAnalysisError,
  ] = useState("");

  const [stories, setStories] =
    useState<CanonEntity[]>([]);

  const [
    storiesLoading,
    setStoriesLoading,
  ] = useState(true);

  const [
    storiesError,
    setStoriesError,
  ] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadStories() {
      setStoriesLoading(true);
      setStoriesError("");

      try {
        const result =
          await Numeria.story.list();

        if (!cancelled) {
          setStories(result);
        }
      } catch (caughtError) {
        if (!cancelled) {
          setStoriesError(
            caughtError instanceof Error
              ? caughtError.message
              : "Failed to load Story Forge content.",
          );
        }
      } finally {
        if (!cancelled) {
          setStoriesLoading(false);
        }
      }
    }

    void loadStories();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredStories = useMemo(() => {
    const normalized =
      query.trim().toLowerCase();

    if (!normalized) {
      return stories;
    }

    return stories.filter(
      (story) =>
        story.name
          .toLowerCase()
          .includes(normalized) ||
        story.id
          .toLowerCase()
          .includes(normalized),
    );
  }, [query, stories]);

  const selectedStory =
    selectedEntity &&
    (
      selectedEntity.type === "Story" ||
      selectedEntity.type === "Scene"
    )
      ? selectedEntity
      : filteredStories.find(
          (story) =>
            story.id === selectedId,
        ) ??
        filteredStories[0] ??
        null;


  useEffect(() => {
    setAnalysis(null);
    setAnalysisError("");
  }, [selectedStory?.id]);

  async function analyzeSelectedStory() {
    if (!selectedStory) {
      return;
    }

    setAnalysisLoading(true);
    setAnalysisError("");

    try {
      const result =
        await Numeria.director.analyzeStory(
          selectedStory.id,
        );

      setAnalysis(result);
    } catch (caughtError) {
      setAnalysisError(
        caughtError instanceof Error
          ? caughtError.message
          : "Story analysis failed.",
      );
    } finally {
      setAnalysisLoading(false);
    }
  }

  const libraryItems = filteredStories.map(
    (story) => ({
      id: story.id,
      name: story.name,
      type: story.type,
      description: readText(
        story,
        "summary",
        "A story from the living Numeria canon.",
      ),
    }),
  );

  const library = (
    <EntityLibrary
      eyebrow="STORY FORGE"
      title="Story Library"
      description="Shape the adventures that bring mathematics to life."
      entities={libraryItems}
      selectedId={
        selectedStory?.id ?? null
      }
      actionLabel="+ Forge Story"
      emptyTitle={
        storiesLoading
          ? "Loading stories..."
          : storiesError
            ? "Story Forge could not load"
            : "No stories yet"
      }
      emptyDescription={
        storiesError ||
        "Create the first adventure in the Numeria universe."
      }
      renderIcon={() => "📖"}
      onSelect={selectEntity}
      onAction={onCreateStory}
    />
  );

  const toolbar = (
    <ForgeToolbar
      search={
        <SearchBar
          value={query}
          placeholder="Search stories and scenes..."
          onChange={setQuery}
        />
      }
      actions={
        <Button
          onClick={onCreateStory}
          disabled={!onCreateStory}
        >
          + Forge Story
        </Button>
      }
    />
  );

  return (
    <ForgeLayout
      library={library}
      toolbar={toolbar}
      libraryLabel="Story Forge library"
      canvasLabel="Story Forge canvas"
      className="story-forge-layout"
    >
      {selectedStory ? (
        <>
          <section className="story-forge-hero">
            <div className="story-forge-symbol">
              📖
            </div>

            <div>
              <Badge tone="brand">
                {selectedStory.type}
              </Badge>

              <h2>{selectedStory.name}</h2>

              <p>
                {readText(
                  selectedStory,
                  "summary",
                  "This story is waiting for its next chapter.",
                )}
              </p>
            </div>
          </section>

          <section className="story-forge-grid">
            <Card
              title="Learning Goal"
              description="The mathematical understanding this story develops."
            >
              <p>
                {readText(
                  selectedStory,
                  "educational_mission",
                  "No learning goal has been documented yet.",
                )}
              </p>
            </Card>

            <Card
              title="Story Status"
              description="Current position in the canon workflow."
            >
              <p>
                {readText(
                  selectedStory,
                  "status",
                  "CANON",
                )}
              </p>
            </Card>

            <Card
              title="Characters"
              description="Heroes participating in this adventure."
            >
              <p>
                Character connections will appear here.
              </p>
            </Card>

            <Card
              title="Location"
              description="Where this adventure takes place."
            >
              <p>
                World and region connections will appear here.
              </p>
            </Card>
          </section>

          <DirectorPanel
            analysis={analysis}
            loading={analysisLoading}
            error={analysisError}
            onAnalyze={() =>
              void analyzeSelectedStory()
            }
          />

          <Card
            title="Story Timeline"
            description="Scenes will eventually appear here as a visual sequence."
          >
            <div className="story-timeline-placeholder">
              <span>Origin</span>
              <i />
              <span>Challenge</span>
              <i />
              <span>Discovery</span>
              <i />
              <span>Resolution</span>
            </div>
          </Card>
        </>
      ) : (
        <Card
          title="Forge the First Story"
          description="Create an adventure that transforms a mathematical idea into a memorable experience."
        >
          <Button
            onClick={onCreateStory}
            disabled={!onCreateStory}
          >
            + Forge Story
          </Button>
        </Card>
      )}
    </ForgeLayout>
  );
}
