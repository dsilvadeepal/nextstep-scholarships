import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { test, expect, vi } from "vitest";
import { ChatPanel } from "../components/ChatPanel";
test("chat failure leaves profile and browsing intact and never persists conversation", async () => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));
  render(
    <ChatPanel
      profile={{ grade: 11, graduation_year: null, gpa: null }}
      programIds={[]}
      corpusVersion="v"
      hypothetical={false}
    />,
  );
  fireEvent.click(
    screen.getByRole("button", { name: "Ask about scholarships" }),
  );
  fireEvent.change(screen.getByLabelText("Your question"), {
    target: { value: "What should I prepare?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Ask" }));
  await waitFor(() =>
    expect(screen.getByRole("alert")).toHaveTextContent("still browse"),
  );
  expect(localStorage.length).toBe(0);
  vi.unstubAllGlobals();
});
