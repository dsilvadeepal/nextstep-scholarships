import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";
import { ChatPanel } from "../components/ChatPanel";
import { request } from "../api";
vi.mock("../api", () => ({ request: vi.fn() }));
beforeEach(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});
test("explanations are separate from original sources and deferred official links", async () => {
  vi.mocked(request).mockResolvedValue({
    blocks: [
      {
        text: "Your number is below the published minimum.",
        kind: "explanation",
        evidence_ids: ["c"],
      },
    ],
    gaps: ["Confirm the GPA scale."],
    corpus_version: "v",
    method: "hybrid",
    retrieval_policy: "targeted",
    source_links: [
      { title: "Official regulations", url: "https://example.org/regulations" },
    ],
    evidence: {
      chunks: [
        {
          id: "c",
          heading: "Official minimum",
          source_id: "source",
          text: "The minimum is 3.80.",
          evidence: [],
        },
      ],
    },
  });
  render(
    <ChatPanel
      profile={{ grade: null, graduation_year: null, gpa: null }}
      programIds={["p"]}
      corpusVersion="v"
      hypothetical={false}
    />,
  );
  fireEvent.click(screen.getByText("Ask about scholarships"));
  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "Does my GPA meet the rule?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask" }));
  await waitFor(() =>
    expect(
      screen.getByText("Your number is below the published minimum."),
    ).toBeVisible(),
  );
  expect(
    screen.getByText("Your number is below the published minimum.").tagName,
  ).toBe("P");
  expect(screen.getByText("The minimum is 3.80.")).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Official regulations" }),
  ).toHaveAttribute("href", "https://example.org/regulations");
  expect(screen.getByText("Confirm the GPA scale.")).toBeVisible();
});
