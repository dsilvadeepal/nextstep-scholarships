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
        evidence_ids: ["c", "c2"],
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
          evidence: [
            {
              id: "r1",
              url: "https://example.org/rules",
              section_id: "minimum",
              quote: "The minimum is 3.80.",
            },
          ],
        },
        {
          id: "c2",
          heading: "Another rule",
          source_id: "source",
          text: "Official scores are required.",
          evidence: [
            {
              id: "r2",
              url: "https://example.org/rules",
              section_id: "scores",
              quote: "Official scores are required.",
            },
          ],
        },
      ],
    },
  });
  render(
    <ChatPanel
      profile={{ grade: null, graduation_year: null, gpa: null }}
      programIds={["p"]}
      corpusVersion="v"
      promptRequest={null}
    />,
  );
  fireEvent.click(
    screen.getByRole("button", { name: "Ask about scholarships" }),
  );
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
  expect(screen.queryByText("The minimum is 3.80.")).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Sources (2)" }));
  expect(screen.getByText("The minimum is 3.80.")).toBeInTheDocument();
  expect(
    screen.getAllByRole("link", { name: "Open official source" })[1],
  ).toHaveAttribute("href", "https://example.org/regulations");
  expect(screen.getByText("Confirm the GPA scale.")).toBeVisible();
  expect(screen.getByText("Official scores are required.")).toBeVisible();
});
