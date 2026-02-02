export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Project = {
  id: string;
  name: string;
  created_at: string;
};

export type Dataset = {
  id: string;
  project_id: string;
  filename: string;
  created_at: string;
  profile: Record<string, unknown>;
};

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load projects");
  return res.json();
}

export async function createProject(name: string): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function fetchDatasets(projectId: string): Promise<Dataset[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/datasets`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load datasets");
  return res.json();
}

export async function uploadDataset(projectId: string, file: File): Promise<Dataset> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/projects/${projectId}/datasets`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Failed to upload dataset");
  return res.json();
}

export async function fetchRuns(projectId: string) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/runs`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load runs");
  return res.json();
}

export async function fetchPreview(datasetId: string) {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/preview`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load preview");
  return res.json();
}
