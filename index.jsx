import React, { useState } from 'react';
import { Search, Building2, Briefcase, FileText, Calendar, Filter, ExternalLink, Bookmark, CheckCircle2, ChevronRight, BookOpen, Award, Layers } from 'lucide-react';

const MOCK_JOBS = [
  {
    id: 1,
    title: "2026년 하반기 방산원가 및 재무회계 인턴십",
    company: "한화에어로스페이스",
    tier: "체계업체 (1티어)",
    location: "서울 / 창원",
    type: "채용연계형 인턴",
    categories: ["원가", "회계"],
    keywords: ["방산원가", "제700호", "K-IFRS", "SAP"],
    deadline: "2026.10.15",
    description: "방위산업체 원가 계산 및 방산원가 제57조/제700호 기준 원가검증 지원, K-IFRS 기반 재무제표 작성 보조.",
    qualifications: "상경계열 전공자 우대, 방산원가관리사 자격 보유자 우대, 회계 관련 자격증 우대"
  },
  {
    id: 2,
    title: "재무기획 및 세무 전산 회계 인턴 모집",
    company: "LIG넥스원",
    tier: "체계업체 (1티어)",
    location: "판교 / 용인",
    type: "체험형 인턴",
    categories: ["재무", "세법"],
    keywords: ["조특법", "세무조정", "자금계획", "부가세 영세율"],
    deadline: "2026.10.20",
    description: "방위산업 관련 조세특례제한법(조특법) 세액공제 검토 지원 및 방산물자 수출입 관세·영세율 신고 보조.",
    qualifications: "세무/회계 관련 학과 우대, CPA/CTA 1차 합격자 우대"
  },
  {
    id: 3,
    title: "방산 원가관리 및 관리회계 동계 인턴",
    company: "한국항공우주산업 (KAI)",
    tier: "체계업체 (1티어)",
    location: "사천 / 서울",
    type: "채용연계형 인턴",
    categories: ["원가"],
    keywords: ["원가분석", "방산원가제도", "제안원가", "MRO"],
    deadline: "2026.10.30",
    description: "항공기 제조 및 MRO 사업 부문 제안원가 산정 및 프로젝트별 원가 집계, 원가 적정성 검토 지원.",
    qualifications: "경영/회계/산업공학 전공자, Excel 활용 능력 우수자"
  },
  {
    id: 4,
    title: "재무회계 및 내부회계관리제도(ICFR) 인턴",
    company: "현대로템",
    tier: "체계업체 (1티어)",
    location: "창원 / 의왕",
    type: "체험형 인턴",
    categories: ["회계", "재무"],
    keywords: ["ICFR", "JE Test", "K-IFRS 1115", "주석공시"],
    deadline: "2026.11.05",
    description: "수주산업(K-IFRS 1115호) 진행기준 수익인식 검토 지원, 내부회계관리제도(ICFR) 통제 테스트 보조.",
    qualifications: "상경계열 전공, 회계감사/재무회계 이수자 우대"
  }
];

export default function App() {
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [bookmarks, setBookmarks] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);

  const categories = [
    { id: 'ALL', name: '전체 공고' },
    { id: '원가', name: '원가 (방산원가)' },
    { id: '회계', name: '회계 (K-IFRS/ICFR)' },
    { id: '재무', name: '재무 / 자금' },
    { id: '세법', name: '세법 / 관세' },
  ];

  const filteredJobs = MOCK_JOBS.filter(job => {
    const matchesCategory = selectedCategory === 'ALL' || job.categories.includes(selectedCategory);
    const matchesSearch = job.title.includes(searchQuery) || 
                          job.company.includes(searchQuery) || 
                          job.keywords.some(k => k.includes(searchQuery));
    return matchesCategory && matchesSearch;
  });

  const toggleBookmark = (id, e) => {
    e.stopPropagation();
    setBookmarks(prev => 
      prev.includes(id) ? prev.filter(bId => bId !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans">
      {/* Header */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-30">
        <div className="max-w-6xl mx-mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">DefFinance</h1>
              <p className="text-xs text-slate-400">방위산업 특화 회계·재무·원가 인턴십 포털</p>
            </div>
          </div>
          <div className="text-xs bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-full text-slate-300">
            실시간 등록 공고 <span className="text-blue-400 font-semibold">{MOCK_JOBS.length}</span>건
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Search & Filter Bar */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="기업명, 직무 키워드 (예: 방산원가, K-IFRS, 조특법) 검색"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>
          </div>

          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2">
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  selectedCategory === cat.id
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Job List */}
        <div className="grid gap-4">
          {filteredJobs.map(job => (
            <div
              key={job.id}
              onClick={() => setSelectedJob(job)}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-300 hover:shadow-md transition-all cursor-pointer relative group"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md border border-slate-200">
                      {job.company}
                    </span>
                    <span className="text-xs font-medium px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md border border-blue-100">
                      {job.type}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {job.title}
                  </h3>
                  <div className="flex items-center gap-4 text-xs text-slate-500 flex-wrap">
                    <span className="flex items-center gap-1"><Building2 className="w-3.5 h-3.5" /> {job.tier}</span>
                    <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> 마감일: {job.deadline}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between md:justify-end gap-3 pt-4 md:pt-0 border-t md:border-0 border-slate-100">
                  <button
                    onClick={(e) => toggleBookmark(job.id, e)}
                    className={`p-2.5 rounded-xl border transition-all ${
                      bookmarks.includes(job.id)
                        ? 'bg-amber-50 border-amber-200 text-amber-600'
                        : 'bg-slate-50 border-slate-200 text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    <Bookmark className="w-5 h-5 fill-current" />
                  </button>
                  <button className="flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 px-4 py-2.5 rounded-xl transition-all">
                    상세보기 <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Keywords */}
              <div className="mt-4 pt-4 border-t border-slate-100 flex flex-wrap gap-1.5">
                {job.keywords.map((kw, i) => (
                  <span key={i} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                    #{kw}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Modal Detail */}
      {selectedJob && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-xl">
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded">
                  {selectedJob.company}
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-2">{selectedJob.title}</h2>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-slate-400 hover:text-slate-600 p-2 text-lg"
              >
                ✕
              </button>
            </div>

            <div className="space-y-6 my-6 border-y border-slate-100 py-6">
              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-blue-600" /> 주요 업무 내용
                </h4>
                <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl">
                  {selectedJob.description}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-blue-600" /> 자격 요건 및 우대 사항
                </h4>
                <p className="text-sm text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl">
                  {selectedJob.qualifications}
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setSelectedJob(null)}
                className="px-5 py-2.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                닫기
              </button>
              <button
                onClick={() => alert("지원 페이지로 이동합니다.")}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold shadow-md shadow-blue-500/20"
              >
                공식 지원 페이지 이동
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ShieldCheck(props) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}
