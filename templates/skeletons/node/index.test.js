import test from "node:test";
import assert from "node:assert";
import app from "./index.js";

const server = app.listen(0);
const base = `http://127.0.0.1:${server.address().port}`;

test("healthz responde ok", async () => {
  const r = await fetch(base + "/healthz");
  assert.equal(r.status, 200);
});

test("exemplo responde", async () => {
  const r = await fetch(base + "/api/exemplo");
  assert.equal(r.status, 200);
});

server.close();
