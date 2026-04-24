import { createBrowserRouter } from "react-router";
import { Root } from "./components/Root";
import { Onboarding } from "./components/Onboarding";
import { Dashboard } from "./components/Dashboard";
import { AIAdvisory } from "./components/AIAdvisory";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Onboarding },
      { path: "dashboard", Component: Dashboard },
      { path: "advisory", Component: AIAdvisory },
    ],
  },
]);
