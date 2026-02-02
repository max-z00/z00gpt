"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createProject, fetchProjects, Project } from "./lib/api";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const loadProjects = async () => {
    try {
      const data = await fetchProjects();
      setProjects(data);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    void loadProjects();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    try {
      const project = await createProject(name);
      setProjects([project, ...projects]);
      setName("");
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="space-y-8">
      <section className="card">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="label">Create project</p>
            <h1 className="text-2xl font-semibold">Projects</h1>
            <p className="text-sm text-slate-400">
              Organize datasets, chat sessions, and run history in one place.
            </p>
          </div>
          <div className="flex w-full max-w-md items-center gap-3">
            <input
              className="input"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="New project name"
              aria-label="New project name"
            />
            <button className="button" onClick={handleCreate}>
              Create
            </button>
          </div>
        </div>
        {error ? <p className="mt-4 text-sm text-rose-400">{error}</p> : null}
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        {projects.length === 0 ? (
          <div className="card">
            <p className="text-sm text-slate-400">
              No projects yet. Create one to upload datasets and chat with the LLM.
            </p>
          </div>
        ) : (
          projects.map((project) => (
            <Link key={project.id} href={`/projects/${project.id}`} className="card">
              <h2 className="text-lg font-semibold text-white">{project.name}</h2>
              <p className="text-xs text-slate-400">{project.created_at}</p>
            </Link>
          ))
        )}
      </section>
    </div>
  );
}
