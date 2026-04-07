import { build } from 'esbuild'
import { resolve } from 'path'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = resolve(__dirname, '..')

await build({
  entryPoints: [
    resolve(root, 'electron/main.ts'),
    resolve(root, 'electron/preload.ts'),
  ],
  bundle: true,
  platform: 'node',
  external: ['electron'],
  outdir: resolve(root, 'electron/dist'),
  tsconfig: resolve(root, 'electron/tsconfig.json'),
  nodePaths: [resolve(root, 'renderer/node_modules')],
})

console.log('Electron build complete')
