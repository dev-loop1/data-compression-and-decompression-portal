import React, { useState, useCallback } from 'react';
import { UploadCloud, File, Activity, HelpCircle, Download, XCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';

// --- Helper Components ---

const StatCard = ({ label, value, icon }) => (
    <div className="bg-slate-700/50 rounded-lg p-4 flex items-center">
        <div className="bg-slate-800 p-3 rounded-md mr-4">
            {icon}
        </div>
        <div>
            <p className="text-sm text-slate-400">{label}</p>
            <p className="text-xl font-semibold text-white">{value}</p>
        </div>
    </div>
);

const AlgorithmInfo = ({ algorithm }) => {
    const info = {
        'huffman': {
            name: 'Huffman Coding',
            description: 'A lossless algorithm that assigns variable-length codes to characters based on their frequency. More common characters get shorter codes. Excellent for text files and is often used after an algorithm like LZ77.'
        },
        'rle': {
            name: 'Run-Length Encoding (RLE)',
            description: 'A simple lossless compression where runs of data (e.g., AAAA) are stored as a single value and count (4A). It is only effective for files with long sequences of repeating characters, like simple bitmap images.'
        }
    };

    const currentInfo = info[algorithm];

    return (
        <div className="bg-slate-800 rounded-lg p-6 mt-6 border border-slate-700">
            <h3 className="text-lg font-bold text-cyan-400 flex items-center"><HelpCircle size={20} className="mr-2" />How {currentInfo.name} Works</h3>
            <p className="text-slate-300 mt-2 text-sm">{currentInfo.description}</p>
        </div>
    );
};

// --- Main App Component ---

export default function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [algorithm, setAlgorithm] = useState('huffman'); // Default to Huffman
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [mode, setMode] = useState('compress');

    const handleFileChange = (e) => {
        setStats(null);
        setError('');
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
        }
    };

    const resetState = () => {
        setSelectedFile(null);
        setStats(null);
        setError('');
        setIsLoading(false);
        const fileInput = document.getElementById('file-upload-input');
        if (fileInput) {
            fileInput.value = "";
        }
    };

    const handleProcessFile = useCallback(async () => {
        if (!selectedFile) {
            setError('Please select a file first.');
            return;
        }

        setIsLoading(true);
        setError('');
        setStats(null);

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('algorithm', algorithm);

        const url = `http://localhost:5001/api/${mode}`;

        try {
            const response = await axios.post(url, formData, {
                responseType: 'blob',
            });

            if (mode === 'compress') {
                const statsHeader = response.headers['x-compression-stats'];
                if (statsHeader) {
                    setStats(JSON.parse(statsHeader));
                }
            } else {
                 setStats({ action: 'Decompressed successfully!' });
            }

            const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = downloadUrl;
            
            const contentDisposition = response.headers['content-disposition'];
            let filename = mode === 'compress' ? 'compressed-file' : 'decompressed-file';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }
            
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);

        } catch (err) {
            if (err.response && err.response.data) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorJson = JSON.parse(reader.result);
                        setError(errorJson.error || 'An unknown error occurred.');
                    } catch (e) {
                        setError('An unreadable error response was received from the server.');
                    }
                };
                reader.readAsText(err.response.data);
            } else {
                setError(err.message || 'Failed to connect to the server.');
            }
        } finally {
            setIsLoading(false);
        }
    }, [selectedFile, algorithm, mode]);

    const formatBytes = (bytes = 0, decimals = 2) => {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    return (
        <div className="bg-slate-900 min-h-screen text-white font-sans flex items-center justify-center p-4">
            <div className="w-full max-w-4xl mx-auto">
                <header className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-cyan-400">Data Compression & Decompression Tool</h1>
                    <p className="text-slate-400 mt-2">Upload a file and choose the desired algorithm for compression or decompression</p>
                </header>

                <main className="bg-slate-800/50 p-8 rounded-xl shadow-2xl border border-slate-700">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* Left Side: Controls */}
                        <div>
                            <div className="flex bg-slate-700 rounded-lg p-1 mb-6">
                                <button onClick={() => { setMode('compress'); resetState(); }} className={`w-1/2 p-2 rounded-md font-semibold transition-all ${mode === 'compress' ? 'bg-cyan-500' : 'hover:bg-slate-600'}`}>Compress</button>
                                <button onClick={() => { setMode('decompress'); resetState(); }} className={`w-1/2 p-2 rounded-md font-semibold transition-all ${mode === 'decompress' ? 'bg-indigo-500' : 'hover:bg-slate-600'}`}>Decompress</button>
                            </div>
                            <label htmlFor="file-upload-input" className="cursor-pointer">
                                <div className="border-2 border-dashed border-slate-600 rounded-lg p-10 text-center hover:border-cyan-400 transition-colors">
                                    <UploadCloud className="mx-auto h-12 w-12 text-slate-500" />
                                    <p className="mt-2 text-slate-300"><span className="font-semibold text-cyan-400">Click to upload</span> or drag and drop</p>
                                </div>
                                <input id="file-upload-input" type="file" className="hidden" onChange={handleFileChange} />
                            </label>
                            {selectedFile && (
                                <div className="mt-4 bg-slate-700 p-3 rounded-lg flex justify-between items-center">
                                    <div className="flex items-center truncate"><File size={20} className="text-cyan-400 mr-3 flex-shrink-0" /><span className="text-sm truncate">{selectedFile.name}</span></div>
                                    <button onClick={resetState} className="text-slate-400 hover:text-white flex-shrink-0"><XCircle size={18} /></button>
                                </div>
                            )}
                            <div className="mt-6">
                                <label className="block text-sm font-medium text-slate-300 mb-2">Select Algorithm</label>
                                <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)} className="w-full bg-slate-700 border-slate-600 rounded-md p-3 focus:ring-2 focus:ring-cyan-500">
                                    <option value="huffman">Huffman Coding</option>
                                    <option value="rle">Run-Length Encoding (RLE)</option>
                                </select>
                            </div>
                            <div className="mt-6">
                                <button onClick={handleProcessFile} disabled={!selectedFile || isLoading} className={`w-full p-4 rounded-lg font-bold text-lg flex items-center justify-center transition-all disabled:cursor-not-allowed disabled:bg-slate-600 ${isLoading ? 'bg-yellow-500 text-slate-800' : mode === 'compress' ? 'bg-cyan-500 hover:bg-cyan-600' : 'bg-indigo-500 hover:bg-indigo-600'}`}>
                                    {isLoading ? <><RefreshCw size={24} className="animate-spin mr-3" />Processing...</> : <>{mode === 'compress' ? 'Compress' : 'Decompress'} & Download <Download size={24} className="ml-3" /></>}
                                </button>
                            </div>
                        </div>
                        {/* Right Side: Results & Info */}
                        <div>
                            <h2 className="text-2xl font-bold mb-4 flex items-center"><Activity size={24} className="mr-2" />Results</h2>
                            <div className="bg-slate-900/70 p-6 rounded-lg min-h-[250px] flex items-center justify-center">
                                {isLoading && <p className="text-slate-400">Processing your file...</p>}
                                {error && <p className="text-red-400 text-center">{error}</p>}
                                {stats && !error && (mode === 'compress' ? (
                                    <div className="grid grid-cols-2 gap-4 w-full">
                                        <StatCard label="Original Size" value={formatBytes(stats.originalSize)} icon={<File className="text-blue-400" />} />
                                        <StatCard label="Compressed Size" value={formatBytes(stats.compressedSize)} icon={<File className="text-green-400" />} />
                                        <StatCard label="Processing Time" value={`${stats.processingTime} ms`} icon={<Activity className="text-yellow-400" />} />
                                        <StatCard label="Ratio" value={`${stats.compressionRatio}%`} icon={<Download className="text-purple-400" />} />
                                    </div>
                                ) : (
                                    <div className="text-center text-green-400"><h3 className="text-xl font-bold">File Decompressed!</h3><p>Your download has started.</p></div>
                                ))}
                                {!isLoading && !error && !stats && <p className="text-slate-500">Statistics will appear here.</p>}
                            </div>
                            <AlgorithmInfo algorithm={algorithm} />
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
