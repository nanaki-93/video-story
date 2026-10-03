import { defineConfig } from "vite";

export default defineConfig({
  build: {
    target: ["safari17", "chrome120"],
    commonjsOptions: {
      include: [/node_modules/, /generated\/validators\.cjs$/],
    },
  },
});
