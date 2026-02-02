"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchPreview } from "../../../../lib/api";

export default function DatasetPreviewPage() {
  const params = useParams<{ id: string; datasetId: string }>();
  const datasetId = params?.datasetId as string;
  const projectId = params?.id as string;
  const [preview, setPreview] = useState<{ columns: string[]; rows: any[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchPreview(datasetId);
        setPreview(data);
      } catch (err) {
        setError((err as Error).message);
      }
    };
    void load();
  }, [datasetId]);

  return (
    <div className="space-y-4">
      <Link href={`/projects/${projectId}`} className="text-sm text-indigo-300">
        ← Back to project
      </Link>
      <div className="card">
        <p className="label">Dataset preview</p>
        {error ? <p className="text-sm text-rose-400">{error}</p> : null}
        {preview ? (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-slate-200">
              <thead className="bg-slate-900">
                <tr>
                  {preview.columns.map((col) => (
                    <th key={col} className="px-2 py-1 text-left font-medium">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, rowIndex) => (
                  <tr key={rowIndex} className="border-t border-slate-800">
                    {preview.columns.map((col) => (
                      <td key={col} className="px-2 py-1">
                        {String(row[col] ?? "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-400">Loading preview...</p>
        )}
      </div>
    </div>
  );
}
