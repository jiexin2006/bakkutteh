import { createBrowserRouter } from "react-router";
import { Root } from "./components/Root";
import { EntryGate } from "./components/EntryGate";
import { Onboarding } from "./components/Onboarding";
import { Dashboard } from "./components/Dashboard";
import { AIAdvisory } from "./components/AIAdvisory";
import { ProfileSelector } from "./components/ProfileSelector";
import { ProfileSettings } from "./components/ProfileSettings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: EntryGate },
      { path: "onboarding", Component: Onboarding },
      { path: "profiles", Component: ProfileSelector },
      { path: "profile", Component: ProfileSettings },
      { path: "dashboard", Component: Dashboard },
      { path: "advisory", Component: AIAdvisory },
    ],
  },
]);
