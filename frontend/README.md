# Philippine Legal Assistant Frontend

A modern web interface for the Philippine Legal Assistant, built with Next.js, TypeScript, and Tailwind CSS. This application provides an intuitive interface for querying and analyzing Philippine Supreme Court decisions.

## Features

- 🔍 Semantic search across legal documents
- 📚 Context-aware answers from legal texts
- 🎨 Modern, responsive UI with dark mode support
- ⚡ Real-time search results
- 📱 Mobile-friendly design
- 🌙 Dark mode support
- 🎯 Relevant passage highlighting
- 📄 Source document citations

## Tech Stack

- [Next.js 14](https://nextjs.org/) - React framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Shadcn UI](https://ui.shadcn.com/) - UI components
- [Lucide Icons](https://lucide.dev/) - Icons
- [next-themes](https://github.com/pacocoursey/next-themes) - Dark mode

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── page.tsx        # Home page
│   │   ├── layout.tsx      # Root layout
│   │   └── globals.css     # Global styles
│   ├── components/         # React components
│   │   ├── ui/            # Shadcn UI components
│   │   └── theme-provider.tsx
│   └── lib/               # Utility functions
├── public/                # Static files
└── tailwind.config.ts    # Tailwind configuration
```

## Development

- The application uses the App Router in Next.js 14
- Styling is done with Tailwind CSS and Shadcn UI components
- Dark mode is implemented using next-themes
- Components are built with TypeScript for type safety

## API Integration

The frontend connects to a FastAPI backend at `http://localhost:8000` which provides:

- Document search functionality
- Question answering capabilities
- Document analysis features

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Shadcn UI](https://ui.shadcn.com/)
- Icons from [Lucide](https://lucide.dev/)
- Styling with [Tailwind CSS](https://tailwindcss.com/)
