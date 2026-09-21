import express from "express";

const app = express();
app.use(express.json({ limit: "256kb" }));

app.get("/healthz", (_req, res) => res.json({ status: "ok" }));
app.get("/api/exemplo", (_req, res) =>
  res.json({ mensagem: "troque esta rota pelo seu domínio (consulte ARCHITETURA-DADOS.md)" })
);

if (process.env.NODE_ENV !== "test") {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`{{NOME}} ouvindo em :${PORT}`));
}

export default app;
