import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
const [loading, setLoading] = useState(false)
const [sidebarInfo, setSidebarInfo] = useState({
  cacheHit: null,
  model: null,
  usage: null,
})

  return (
    <>
      <div className="flex h-screen">
        <aside className='w-64'>...</aside>

        <main className='flex flex-col flex-1'>
          <div className='flex overflow-y-auto ...'>
            ...
          </div>

          <div className='area-text'>
            <textarea  className='flex-1 resize-none border round-lg p-3 focus:outline-none'/>
            <button className='bg-blue-600' text-white px-4 py-2 rounded-lg hover:bg-blue-700> Enviar</button>
          </div>
          
        </main>

      </div>
    </>
  )
}

export default App
