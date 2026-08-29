# OMNIX Frontend - Sci-Fi/Cyberpunk UI

This is the React/TypeScript + Tailwind CSS frontend for the Omnix Gaming Companion, featuring a futuristic Sci-Fi/Cyberpunk aesthetic.

## Tech Stack

- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Fonts:**
  - Orbitron (HUD/Headers)
  - Rajdhani (Body Text)

## Features

### Visual Design
- 🎨 Neon blue (#00f3ff) and red (#ff2a2a) color scheme
- 🌌 Deep space background (#050b14)
- ✨ Glowing borders and shadows
- 🔮 Glassmorphism panels with backdrop blur
- ⚡ Smooth animations and transitions
- 🎯 Custom scrollbars

### UI Components
- **HUD Panel** - Reusable container with corner accents
- **Chat Interface** - Message bubbles with animations
- **Game Status Display** - Rotating circular indicator
- **Settings Panel** - Hover effects and transitions
- **AI Provider Selector** - Radio button groups
- **Stats Display** - Grid layout with hexagon centerpiece

## Setup Instructions

### Prerequisites
- Node.js 20.19+ (or 22.12+) and npm/yarn - required by the installed Vite version

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

### Development

Start the development server:
```bash
npm run dev
# or
yarn dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:
```bash
npm run build
# or
yarn build
```

The build output will be in the `dist/` directory.

### Preview Production Build

Preview the production build locally:
```bash
npm run preview
# or
yarn preview
```

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx           # Main HUD component
│   ├── main.tsx          # React entry point
│   └── index.css         # Global styles + Tailwind
├── index.html            # HTML entry point
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── tailwind.config.js    # Tailwind theme customization
├── vite.config.ts        # Vite build configuration
└── README.md             # This file
```

## Customization

### Colors

Edit `tailwind.config.js` to customize the color palette:

```javascript
colors: {
  omnix: {
    dark: '#050b14',      // Background
    panel: 'rgba(10, 20, 40, 0.7)', // Panel background
    blue: '#00f3ff',      // Primary accent
    blueDim: 'rgba(0, 243, 255, 0.1)', // Dim blue
    red: '#ff2a2a',       // Secondary accent
    text: '#e0f7ff',      // Text color
  },
}
```

### Fonts

Fonts are loaded from Google Fonts in `index.html`:
- **Orbitron** - Futuristic display font for headers
- **Rajdhani** - Clean sans-serif for body text

### Animations

Custom animations are defined in `tailwind.config.js`:
```javascript
animation: {
  'spin-slow': 'spin 8s linear infinite',
}
```

## Key Components

### Panel Component

Reusable HUD panel with corner accents:

```tsx
<Panel title="SETTINGS" className="flex-1">
  {/* Content */}
</Panel>
```

### Layout Grid

The main layout uses a 12-column grid:
- **Columns 1-3:** Chat interface
- **Columns 4-8:** Game status display
- **Columns 9-12:** Settings and AI provider

## Integration with Python Backend

This frontend is designed to work alongside the existing Python/PyQt6 backend. Future integration options:

1. **Electron App:** Embed as desktop application
2. **Web Service:** Run Python backend as API server
3. **WebView:** Embed in PyQt6 QWebEngineView
4. **Hybrid:** Use both UIs depending on platform

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, you can change it in `vite.config.ts`:

```typescript
server: {
  port: 3001, // Change to desired port
}
```

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors

Ensure all dependencies are installed:
```bash
npm install --save-dev @types/react @types/react-dom
```

## Performance

- Vite provides instant hot module replacement (HMR)
- Production builds are optimized with tree-shaking
- Tailwind CSS purges unused styles
- Code splitting for optimal load times

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Same as main Omnix project (see root LICENSE file)

## Contributing

See main project CONTRIBUTING.md

## Resources

- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vite Documentation](https://vitejs.dev/)
- [Lucide Icons](https://lucide.dev/)
- [Orbitron Font](https://fonts.google.com/specimen/Orbitron)
- [Rajdhani Font](https://fonts.google.com/specimen/Rajdhani)
