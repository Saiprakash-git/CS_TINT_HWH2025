export default function Header() {
  return (
    <header className="bg-gray-900 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">Cyber Threat Intelligence</h1>
        <nav className="space-x-4">
          <a href="#" className="hover:text-yellow-400">Dashboard</a>
          <a href="#" className="hover:text-yellow-400">Features</a>
          <a href="#" className="hover:text-yellow-400">About</a>
        </nav>
      </div>
    </header>
  )
}

