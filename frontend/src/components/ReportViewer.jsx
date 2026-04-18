import ReactMarkdown from "react-markdown";

function Skeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      <div className="h-5 bg-gray-300 rounded w-3/4" />
      <div className="h-5 bg-gray-300 rounded w-full" />
      <div className="h-5 bg-gray-300 rounded w-5/6" />
    </div>
  );
}

export default function ReportViewer({ report, pdfUrl, isLoading }) {
  if (isLoading) return <Skeleton />;
  if (!report) return null;

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">📄 Intelligence Report</h2>
        {pdfUrl && (
          <a
            href={pdfUrl}
            download
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
          >
            ⬇️ Download PDF
          </a>
        )}
      </div>

      <div className="px-6 py-6">
        <ReactMarkdown className="prose prose-lg max-w-none">{report}</ReactMarkdown>
      </div>
    </div>
  );
}
