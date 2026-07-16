import StudioApplication from "./StudioApplication";
import { StudioProvider } from "./state";

export default function App() {
  return (
    <StudioProvider>
      <StudioApplication />
    </StudioProvider>
  );
}
