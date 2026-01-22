export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-900">
          Welcome to Meghan
        </h1>
        <p className="text-xl text-center text-gray-600 mb-8">
          AI-powered community support system for young adults
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2 text-primary-600">Talk Mode</h3>
            <p className="text-gray-600">Empathetic listening and emotional validation</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2 text-primary-600">Plan Mode</h3>
            <p className="text-gray-600">Micro-planning and manageable next steps</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2 text-primary-600">Calm Mode</h3>
            <p className="text-gray-600">Grounding techniques and breathing exercises</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2 text-primary-600">Reflect Mode</h3>
            <p className="text-gray-600">Structured journaling and self-reflection</p>
          </div>
        </div>
      </div>
    </main>
  );
}