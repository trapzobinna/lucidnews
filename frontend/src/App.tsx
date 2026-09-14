
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Briefing from './pages/Briefing';
import Goals from './pages/Goals';
import Excluded from './pages/Excluded';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Briefing />} />
          <Route path="/goals" element={<Goals />} />
          <Route path="/excluded" element={<Excluded />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
