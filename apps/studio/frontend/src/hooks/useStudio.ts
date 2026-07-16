import { useContext } from "react";

import {
  StudioContext,
} from "../state/StudioContext";

export default function useStudio() {
  const context =
    useContext(StudioContext);

  if (!context) {
    throw new Error(
      "useStudio must be used inside StudioProvider.",
    );
  }

  return context;
}
