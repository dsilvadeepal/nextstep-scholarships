import { render, screen, fireEvent } from "@testing-library/react";
import { test, expect, vi } from "vitest";
import { ProfileForm } from "../components/ProfileForm";
import { Results } from "../components/Results";

test("all profile fields can be skipped without inventing a GPA", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.click(screen.getByRole("button", { name: "Explore scholarships" }));
  expect(submit.mock.calls[0][0].gpa).toBeNull();
  expect(submit.mock.calls[0][0].grade).toBeNull();
  expect(
    screen.getByRole("button", { name: "Fictional junior" }),
  ).toBeVisible();
});
test("empty catalog explains collection limits", () => {
  render(
    <Results
      scholarships={[]}
      matches={[]}
      onSelect={() => {}}
      selected={[]}
    />,
  );
  expect(screen.getByText(/outside this collection/i)).toBeVisible();
});

test("profile records explicit GPA scale and documentation without inferring admission", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.change(screen.getByLabelText("GPA value"), {
    target: { value: "91" },
  });
  fireEvent.change(screen.getByLabelText("GPA scale"), {
    target: { value: "100" },
  });
  fireEvent.change(screen.getByLabelText("GPA documentation"), {
    target: { value: "documented" },
  });
  fireEvent.change(screen.getByLabelText("Graduation year"), {
    target: { value: "2027" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Explore scholarships" }));
  expect(submit.mock.calls[0][0].gpa).toMatchObject({
    value: 91,
    scale: 100,
    estimated: false,
  });
  expect(submit.mock.calls[0][0].graduation_year).toBe(2027);
  expect(submit.mock.calls[0][0].context?.accepted_colleges).toBeUndefined();
});
