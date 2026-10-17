import { render, screen, fireEvent } from "@testing-library/react";
import { test, expect, vi } from "vitest";
import { ProfileForm } from "../components/ProfileForm";
import { Results } from "../components/Results";

test("all profile fields can be skipped without inventing a GPA", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.click(screen.getByRole("button", { name: "Find my matches" }));
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
      onAsk={() => {}}
    />,
  );
  expect(screen.getByText(/outside this collection/i)).toBeVisible();
});

test("profile records explicit GPA scale and documentation without inferring admission", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.click(screen.getByRole("button", { name: "Edit details" }));
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
  fireEvent.click(screen.getByRole("button", { name: "Find my matches" }));
  expect(submit.mock.calls[0][0].gpa).toMatchObject({
    value: 91,
    scale: 100,
    estimated: false,
  });
  expect(submit.mock.calls[0][0].graduation_year).toBe(2027);
  expect(submit.mock.calls[0][0].context?.accepted_colleges).toBeUndefined();
});

test("short intake uses only reviewed named plan hints and explicit Georgia residency", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.change(screen.getByLabelText("School year"), { target: { value: "11" } });
  fireEvent.change(screen.getByLabelText("Georgia resident?"), { target: { value: "yes" } });
  fireEvent.change(screen.getByLabelText("GPA value"), { target: { value: "3.6" } });
  fireEvent.change(screen.getByLabelText("GPA documentation"), { target: { value: "estimated" } });
  fireEvent.change(screen.getByLabelText(/Tell us a little about your plans/), {
    target: { value: "I'm interested in engineering, considering Georgia Tech and Auburn, and I volunteer." },
  });
  expect(screen.getByText(/Detected mentions: Georgia Tech, Auburn/)).toBeVisible();
  fireEvent.click(screen.getByLabelText("Use these reviewed details in my matches"));
  fireEvent.click(screen.getByRole("button", { name: "Find my matches" }));
  expect(submit.mock.calls[0][0]).toMatchObject({
    grade: 11,
    residence: { state: "GA" },
    gpa: { value: 3.6, estimated: true, scale: null, type: "unknown" },
    prospective_colleges: ["Georgia Tech", "Auburn"],
    interests: ["engineering", "volunteering"],
  });
  expect(submit.mock.calls[0][0].context?.accepted_colleges).toBeUndefined();
  expect(submit.mock.calls[0][0].context?.student_plans).toContain("engineering");
});

test("unknown plans and non-Georgia residency do not invent a state or admission", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.change(screen.getByLabelText("Georgia resident?"), { target: { value: "no" } });
  fireEvent.change(screen.getByLabelText(/Tell us a little about your plans/), {
    target: { value: "I am not considering Auburn and might apply to another college." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Find my matches" }));
  expect(submit.mock.calls[0][0].residence).toEqual({});
  expect(submit.mock.calls[0][0].context).toMatchObject({ georgia_resident: false });
  expect(submit.mock.calls[0][0].prospective_colleges).toEqual([]);
});

test("detected mentions do not become profile facts before confirmation", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.change(screen.getByLabelText(/Tell us a little about your plans/), {
    target: { value: "My sister attends Auburn. I might study engineering." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Find my matches" }));
  expect(submit.mock.calls[0][0].prospective_colleges).toEqual([]);
  expect(submit.mock.calls[0][0].interests).toEqual([]);
  expect(submit.mock.calls[0][0].context?.student_plans).toContain("sister");
});

test("fictional starter updates the visible editable intake", () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.click(screen.getByRole("button", { name: "Fictional senior" }));
  expect(screen.getByLabelText("School year")).toHaveValue("12");
  expect(screen.getByLabelText("Georgia resident?")).toHaveValue("yes");
  expect(screen.getByLabelText("GPA value")).toHaveValue(3.5);
  expect(screen.getByText(/Senior · Georgia resident · Estimated GPA 3.5/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Find my matches" }));
  expect(submit.mock.calls[1][0]).toMatchObject(submit.mock.calls[0][0]);
});

test('reviewed note supplies identity and activities only after confirmation, and edits invalidate confirmation', () => {
  const submit = vi.fn();
  render(<ProfileForm onSubmit={submit} />);
  fireEvent.change(screen.getByLabelText(/Tell us a little/), {target:{value:'I am interested in engineering; I want Georgia Tech and maybe Kennesaw State. I do not have any volunteer experience. But I am part of the Science Olympiad School. I am a Georgia resident and a United States citizen.'}});
  expect(screen.getByLabelText('Review citizenship')).toHaveValue('US citizen');
  expect(screen.getByLabelText('Review colleges')).toHaveValue('Kennesaw State, Georgia Tech');
  expect(screen.getByLabelText('Review volunteer experience')).toHaveValue('none');
  expect(screen.getByLabelText('Review interests')).toHaveValue('engineering');
  expect(screen.getByLabelText('Review activities')).toHaveValue('Science Olympiad');
  fireEvent.click(screen.getByRole('button',{name:'Find my matches'}));
  expect(submit.mock.calls[0][0].context.citizenship).toBeUndefined();
  fireEvent.click(screen.getByLabelText('Use these reviewed details in my matches'));
  fireEvent.click(screen.getByRole('button',{name:'Find my matches'}));
  expect(submit.mock.calls[1][0]).toMatchObject({residence:{state:'GA'},prospective_colleges:['Kennesaw State','Georgia Tech'],interests:['engineering'],context:{citizenship:'US citizen',volunteer_experience:'none',activities:['Science Olympiad']}});
  fireEvent.change(screen.getByLabelText('Review citizenship'),{target:{value:'permanent resident'}});
  expect(screen.getByLabelText('Use these reviewed details in my matches')).not.toBeChecked();
});
