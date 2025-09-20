---
date: "2024-04-10T00:00:00Z"
tags:
- vscode
- tutorial
- nestjs
- webpacko
title: NestJS - Debugging with VS Code
---

I decided to document my debugging set up for NestJS. I had two main prereqs:

* [Hot reload](https://docs.nestjs.com/recipes/hot-reload)
* Debugging inside VSCode

From the hot reload instructions on Nest website, first, add the dependencies:

```bash
yarn add --dev webpack webpack-cli webpack-node-externals ts-loader run-script-webpack-plugin
```

Then I createed a `webpack-hmr-debug.config.js` file:

```javascript
const webpack = require('webpack');
const path = require('path');
const nodeExternals = require('webpack-node-externals');
const { RunScriptWebpackPlugin } = require('run-script-webpack-plugin');

module.exports = {
  entry: ['webpack/hot/poll?100', './src/main.ts'],
  target: 'node',
  devtool: 'source-map',
  externals: [
    nodeExternals({
      allowlist: ['webpack/hot/poll?100'],
    }),
  ],
  module: {
    rules: [
      {
        test: /.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  mode: 'development',
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new RunScriptWebpackPlugin({ name: 'server.js', autoRestart: false }),
  ],
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'server.js',
  },
};
```

Lastly, a new entry on launch.json:

```json
        {
            "type": "node",
            "request": "launch",
            "name": "Debug Nest Framework (Hot Reload)",
            "program": "${workspaceFolder}/node_modules/.bin/webpack",
            "args": ["--config", "webpack-hmr-debug.config.js", "--watch"],
            "sourceMaps": true,
            "cwd": "${workspaceRoot}",
            "console": "integratedTerminal",
        }
```

Main difference from the Hot Reload page on nest website is the the `devtool: 'source-map'` in the webpack config. I lost console output without the `console` line albeit I'm not sure why.
