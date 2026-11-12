import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import typescript from 'typescript'

const source = await readFile(new URL('../src/lib/api.ts', import.meta.url), 'utf8')
const { outputText: code } = typescript.transpileModule(source.replace('import.meta.env.VITE_API_URL', 'undefined'), {
  compilerOptions: { module: typescript.ModuleKind.ESNext, target: typescript.ScriptTarget.ES2022 },
})
const { analyzeDream } = await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`)

test('validation errors are displayed as a helpful message', async () => {
  globalThis.window = globalThis
  const originalFetch = globalThis.fetch
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: [{ msg: 'String too long' }] }), {
    status: 422,
    headers: { 'Content-Type': 'application/json' },
  })
  try {
    await assert.rejects(analyzeDream('a'.repeat(12001), 'auto'), error => {
      assert.equal(error.message, 'تعذر تحليل الحلم. تحقق من النص وحاول مرة أخرى.')
      return true
    })
  } finally {
    globalThis.fetch = originalFetch
  }
})
