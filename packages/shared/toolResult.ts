import { z } from "zod";

export const tableSchema = z.object({
  columns: z.array(z.string()),
  rows: z.array(z.record(z.any())),
  row_count: z.number().optional(),
});

export const chartSchema = z.object({
  type: z.string(),
  x: z.string(),
  y: z.string(),
  data: z.array(z.record(z.any())),
});

export const toolResultSchema = z.object({
  message: z.string(),
  table: tableSchema.optional().nullable(),
  chart: chartSchema.optional().nullable(),
});

export type ToolResult = z.infer<typeof toolResultSchema>;
