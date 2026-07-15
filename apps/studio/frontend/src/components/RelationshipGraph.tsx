import { useMemo } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import type {
  CanonEntity,
  CanonRelationship,
} from "../api";

interface RelationshipGraphProps {
  selectedEntity: CanonEntity;
  neighbors: CanonEntity[];
  relationships: CanonRelationship[];
  onSelectEntity: (entityId: string) => void;
}

interface CanonNodeData extends Record<string, unknown> {
  label: string;
  type: string;
  selected: boolean;
}

function CanonNode({ data }: NodeProps<Node<CanonNodeData>>) {
  return (
    <div
      className={`graph-node ${
        data.selected ? "graph-node-selected" : ""
      }`}
    >
      <Handle type="target" position={Position.Left} />

      <span>{data.type}</span>
      <strong>{data.label}</strong>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = {
  canon: CanonNode,
};

export default function RelationshipGraph({
  selectedEntity,
  neighbors,
  relationships,
  onSelectEntity,
}: RelationshipGraphProps) {
  const nodes = useMemo<Node<CanonNodeData>[]>(() => {
    const centerX = 420;
    const centerY = 220;
    const radiusX = 310;
    const radiusY = 180;

    const centerNode: Node<CanonNodeData> = {
      id: selectedEntity.id,
      type: "canon",
      position: {
        x: centerX,
        y: centerY,
      },
      data: {
        label: selectedEntity.name,
        type: selectedEntity.type,
        selected: true,
      },
    };

    const neighborNodes = neighbors.map((neighbor, index) => {
      const angle =
        (index / Math.max(neighbors.length, 1)) *
        Math.PI *
        2;

      return {
        id: neighbor.id,
        type: "canon",
        position: {
          x: centerX + Math.cos(angle) * radiusX,
          y: centerY + Math.sin(angle) * radiusY,
        },
        data: {
          label: neighbor.name,
          type: neighbor.type,
          selected: false,
        },
      };
    });

    return [centerNode, ...neighborNodes];
  }, [neighbors, selectedEntity]);

  const edges = useMemo<Edge[]>(() => {
    return relationships.map((relationship) => ({
      id: relationship.id,
      source: relationship.source,
      target: relationship.target,
      label: relationship.type.replaceAll("_", " "),
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      animated:
        relationship.source === selectedEntity.id,
      style: {
        strokeWidth: 2,
      },
      labelStyle: {
        fontSize: 10,
        fontWeight: 700,
      },
    }));
  }, [relationships, selectedEntity.id]);

  return (
    <div className="relationship-graph">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.25}
        maxZoom={1.8}
        onNodeClick={(_, node) => {
          if (node.id !== selectedEntity.id) {
            onSelectEntity(node.id);
          }
        }}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
