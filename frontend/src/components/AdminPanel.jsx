import React, { useState, useEffect } from 'react';
import { 
  Database, PlusCircle, Trash2, BookOpen, Layers, Globe, 
  CheckCircle2, AlertCircle, RefreshCw, FileText, Sparkles, Filter, Search 
} from 'lucide-react';

export default function AdminPanel() {
  const [summary, setSummary] = useState(null);
  const [modules, setModules] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState('add-lesson'); // 'add-lesson', 'add-module', 'manage-lessons'
  
  // Status message alerts
  const [alertMsg, setAlertMsg] = useState(null); // { type: 'success' | 'error', text: '' }

  // Add Lesson Form State
  const [lessonForm, setLessonForm] = useState({
    module_id: '',
    title: '',
    content_type: 'Voice Practice',
    difficulty_level: 'FOUNDATIONAL',
    target_text: '',
    phonetic_script: '',
    content_url: ''
  });

  // Add Module Form State
  const [moduleForm, setModuleForm] = useState({
    curriculum_id: '',
    module_name: '',
    sequence_no: 1,
    skill_type: 'Reading & Pronunciation'
  });

  // Search & Filter
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLangFilter, setSelectedLangFilter] = useState('ALL');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sumRes, modRes, lesRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/admin/summary'),
        fetch('http://127.0.0.1:8000/api/admin/modules'),
        fetch('http://127.0.0.1:8000/api/admin/lessons')
      ]);

      if (sumRes.ok) setSummary(await sumRes.json());
      if (modRes.ok) {
        const modData = await modRes.json();
        setModules(modData);
        if (modData.length > 0 && !lessonForm.module_id) {
          setLessonForm(prev => ({ ...prev, module_id: modData[0].module_id }));
        }
      }
      if (lesRes.ok) setLessons(await lesRes.json());
    } catch (err) {
      console.error("Failed to fetch admin data:", err);
      setAlertMsg({ type: 'error', text: 'Could not connect to AksharAI backend server.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (summary?.curriculums?.length > 0 && !moduleForm.curriculum_id) {
      setModuleForm(prev => ({ ...prev, curriculum_id: summary.curriculums[0].curriculum_id }));
    }
  }, [summary]);

  const handleCreateLesson = async (e) => {
    e.preventDefault();
    if (!lessonForm.module_id || !lessonForm.title.trim()) {
      setAlertMsg({ type: 'error', text: 'Please select a module and enter a lesson title.' });
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:8000/api/admin/lessons', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lessonForm)
      });

      const data = await res.json();
      if (res.ok) {
        setAlertMsg({ type: 'success', text: `Lesson "${lessonForm.title}" added successfully!` });
        setLessonForm(prev => ({
          ...prev,
          title: '',
          target_text: '',
          phonetic_script: '',
          content_url: ''
        }));
        fetchData();
      } else {
        setAlertMsg({ type: 'error', text: data.detail || 'Failed to add lesson.' });
      }
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Server connection failed.' });
    }
  };

  const handleCreateModule = async (e) => {
    e.preventDefault();
    if (!moduleForm.curriculum_id || !moduleForm.module_name.trim()) {
      setAlertMsg({ type: 'error', text: 'Please select a curriculum and enter a module name.' });
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:8000/api/admin/modules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(moduleForm)
      });

      const data = await res.json();
      if (res.ok) {
        setAlertMsg({ type: 'success', text: `Module "${moduleForm.module_name}" created successfully!` });
        setModuleForm(prev => ({ ...prev, module_name: '' }));
        fetchData();
      } else {
        setAlertMsg({ type: 'error', text: data.detail || 'Failed to create module.' });
      }
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Server connection failed.' });
    }
  };

  const handleDeleteLesson = async (lessonId, title) => {
    if (!window.confirm(`Are you sure you want to delete lesson "${title}"?`)) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/admin/lessons/${lessonId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        setAlertMsg({ type: 'success', text: `Lesson "${title}" deleted successfully.` });
        fetchData();
      } else {
        setAlertMsg({ type: 'error', text: 'Failed to delete lesson.' });
      }
    } catch (err) {
      setAlertMsg({ type: 'error', text: 'Server connection failed.' });
    }
  };

  const filteredLessons = lessons.filter(l => {
    const matchesSearch = l.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          l.module_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          l.curriculum_title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLang = selectedLangFilter === 'ALL' || l.iso_code === selectedLangFilter;
    return matchesSearch && matchesLang;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-900/40 via-teal-900/30 to-slate-900 border border-emerald-500/30 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <Database size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Admin Content Studio</h2>
              <p className="text-sm text-slate-300">Manage, create, and curate literacy content across all 8 supported languages.</p>
            </div>
          </div>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-slate-200 hover:text-white hover:bg-slate-700 transition-all"
        >
          <RefreshCw size={14} className={loading ? "animate-spin text-emerald-400" : ""} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Alert Messages */}
      {alertMsg && (
        <div className={`p-4 rounded-xl border flex items-center justify-between ${
          alertMsg.type === 'success' 
            ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300' 
            : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
        }`}>
          <div className="flex items-center gap-2 text-sm font-semibold">
            {alertMsg.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            <span>{alertMsg.text}</span>
          </div>
          <button onClick={() => setAlertMsg(null)} className="text-xs opacity-70 hover:opacity-100">Dismiss</button>
        </div>
      )}

      {/* Platform Repository Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
          <Globe size={20} className="mx-auto text-emerald-400 mb-1" />
          <p className="text-2xl font-bold text-white">{summary?.languages_count ?? 8}</p>
          <p className="text-xs text-slate-400 font-medium">Languages</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
          <BookOpen size={20} className="mx-auto text-teal-400 mb-1" />
          <p className="text-2xl font-bold text-white">{summary?.curriculums_count ?? 8}</p>
          <p className="text-xs text-slate-400 font-medium">Curriculums</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
          <Layers size={20} className="mx-auto text-blue-400 mb-1" />
          <p className="text-2xl font-bold text-white">{summary?.modules_count ?? 32}</p>
          <p className="text-xs text-slate-400 font-medium">Modules</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
          <FileText size={20} className="mx-auto text-indigo-400 mb-1" />
          <p className="text-2xl font-bold text-white">{summary?.lessons_count ?? 64}</p>
          <p className="text-xs text-slate-400 font-medium">Lessons</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
          <Sparkles size={20} className="mx-auto text-purple-400 mb-1" />
          <p className="text-2xl font-bold text-white">{summary?.assessments_count ?? 4}</p>
          <p className="text-xs text-slate-400 font-medium">Assessments</p>
        </div>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 text-center">
          <Database size={20} className="mx-auto text-amber-400 mb-1" />
          <p className="text-2xl font-bold text-white">{summary?.learners_count ?? 1}</p>
          <p className="text-xs text-slate-400 font-medium">Learners</p>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubTab('add-lesson')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'add-lesson'
              ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <PlusCircle size={16} />
          <span>Add New Lesson</span>
        </button>

        <button
          onClick={() => setActiveSubTab('add-module')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'add-module'
              ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Layers size={16} />
          <span>Add New Module</span>
        </button>

        <button
          onClick={() => setActiveSubTab('manage-lessons')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
            activeSubTab === 'manage-lessons'
              ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Database size={16} />
          <span>Manage Repository ({lessons.length})</span>
        </button>
      </div>

      {/* SUB-TAB 1: ADD NEW LESSON FORM */}
      {activeSubTab === 'add-lesson' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <PlusCircle className="text-emerald-400" size={20} />
                Create New Content Lesson
              </h3>
              <p className="text-xs text-slate-400">Add practice text, voice prompts, and phonetic scripts under target modules.</p>
            </div>
          </div>

          <form onSubmit={handleCreateLesson} className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Target Module */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Target Module *</label>
              <select
                value={lessonForm.module_id}
                onChange={e => setLessonForm({ ...lessonForm, module_id: parseInt(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              >
                {modules.map(m => (
                  <option key={m.module_id} value={m.module_id}>
                    [{m.iso_code.toUpperCase()}] {m.module_name} ({m.skill_type})
                  </option>
                ))}
              </select>
            </div>

            {/* Lesson Title */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Lesson Title *</label>
              <input
                type="text"
                required
                placeholder="e.g. Daily Greetings & Pronunciation Practice"
                value={lessonForm.title}
                onChange={e => setLessonForm({ ...lessonForm, title: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            {/* Content Type */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Content Type</label>
              <select
                value={lessonForm.content_type}
                onChange={e => setLessonForm({ ...lessonForm, content_type: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              >
                <option value="Voice Practice">Voice Practice</option>
                <option value="Functional Reading">Functional Reading</option>
              </select>
            </div>

            {/* Difficulty Level */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Difficulty Level</label>
              <select
                value={lessonForm.difficulty_level}
                onChange={e => setLessonForm({ ...lessonForm, difficulty_level: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              >
                <option value="FOUNDATIONAL">FOUNDATIONAL</option>
                <option value="FUNCTIONAL">FUNCTIONAL</option>
                <option value="INTERMEDIATE">INTERMEDIATE</option>
                <option value="ADVANCED">ADVANCED</option>
              </select>
            </div>

            {/* Target Practice Text */}
            <div className="space-y-2 md:col-span-2">
              <label className="text-xs font-semibold text-slate-300">Target Practice Text (Native Language Passage)</label>
              <textarea
                rows={3}
                placeholder="Enter reading passage or speech prompt in the native language..."
                value={lessonForm.target_text}
                onChange={e => setLessonForm({ ...lessonForm, target_text: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            {/* Phonetic Script */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Phonetic Script / Syllables Breakdown (JSON)</label>
              <input
                type="text"
                placeholder='["Pho-ne-tic", "Syll-a-ble"]'
                value={lessonForm.phonetic_script}
                onChange={e => setLessonForm({ ...lessonForm, phonetic_script: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none font-mono text-xs"
              />
            </div>

            {/* Audio URL */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Audio Asset URL</label>
              <input
                type="text"
                placeholder="/audio/custom_lesson.mp3"
                value={lessonForm.content_url}
                onChange={e => setLessonForm({ ...lessonForm, content_url: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            {/* Submit Button */}
            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-lg shadow-emerald-600/30 transition-all"
              >
                <PlusCircle size={18} />
                <span>Save Lesson to Repository</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* SUB-TAB 2: ADD NEW MODULE FORM */}
      {activeSubTab === 'add-module' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="text-teal-400" size={20} />
                Create New Module
              </h3>
              <p className="text-xs text-slate-400">Add structured skill modules under any language curriculum.</p>
            </div>
          </div>

          <form onSubmit={handleCreateModule} className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Target Curriculum */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Target Language Curriculum *</label>
              <select
                value={moduleForm.curriculum_id}
                onChange={e => setModuleForm({ ...moduleForm, curriculum_id: parseInt(e.target.value) })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              >
                {summary?.curriculums?.map(c => (
                  <option key={c.curriculum_id} value={c.curriculum_id}>
                    [ID {c.curriculum_id}] {c.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Module Name */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Module Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Advanced Medical & Prescription Literacy"
                value={moduleForm.module_name}
                onChange={e => setModuleForm({ ...moduleForm, module_name: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            {/* Sequence No */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Sequence Number</label>
              <input
                type="number"
                min="1"
                value={moduleForm.sequence_no}
                onChange={e => setModuleForm({ ...moduleForm, sequence_no: parseInt(e.target.value) || 1 })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            {/* Skill Type */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Canonical Skill Type</label>
              <select
                value={moduleForm.skill_type}
                onChange={e => setModuleForm({ ...moduleForm, skill_type: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none"
              >
                <option value="Reading & Pronunciation">Reading & Pronunciation</option>
                <option value="Word Formation">Word Formation</option>
                <option value="Grammar">Grammar</option>
                <option value="Literature">Literature</option>
              </select>
            </div>

            {/* Submit Button */}
            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-sm shadow-lg shadow-teal-600/30 transition-all"
              >
                <Layers size={18} />
                <span>Create Module</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* SUB-TAB 3: MANAGE & DELETE CONTENT TABLE */}
      {activeSubTab === 'manage-lessons' && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Database className="text-emerald-400" size={20} />
                Repository Content Manager
              </h3>
              <p className="text-xs text-slate-400">Search, inspect, and remove lessons from the platform repository.</p>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-64">
                <Search size={16} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search lessons..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <select
                value={selectedLangFilter}
                onChange={e => setSelectedLangFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:border-emerald-500 focus:outline-none"
              >
                <option value="ALL">All Languages</option>
                <option value="en">English (EN)</option>
                <option value="hi">Hindi (HI)</option>
                <option value="te">Telugu (TE)</option>
                <option value="ta">Tamil (TA)</option>
                <option value="bn">Bengali (BN)</option>
                <option value="mr">Marathi (MR)</option>
                <option value="kn">Kannada (KN)</option>
                <option value="es">Spanish (ES)</option>
              </select>
            </div>
          </div>

          {/* Lessons Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Lang</th>
                  <th className="py-3 px-4">Lesson Title</th>
                  <th className="py-3 px-4">Module Name</th>
                  <th className="py-3 px-4">Skill</th>
                  <th className="py-3 px-4">Level</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredLessons.length > 0 ? (
                  filteredLessons.map(l => (
                    <tr key={l.lesson_id} className="hover:bg-slate-800/40 transition-all">
                      <td className="py-3 px-4 text-slate-500 font-mono">#{l.lesson_id}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20 uppercase">
                          {l.iso_code}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-semibold text-white">{l.title}</td>
                      <td className="py-3 px-4 text-slate-300 max-w-xs truncate">{l.module_name}</td>
                      <td className="py-3 px-4 text-slate-400">{l.skill_type}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                          {l.difficulty_level}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleDeleteLesson(l.lesson_id, l.title)}
                          className="p-1.5 rounded-lg bg-rose-950/40 border border-rose-500/30 text-rose-400 hover:bg-rose-900/60 transition-all"
                          title="Delete Lesson"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500">
                      No matching lessons found in repository.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
