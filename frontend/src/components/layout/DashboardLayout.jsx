import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

function DashboardLayout({ children }) {
    return (
        <div className="flex bg-slate-100 min-h-screen">

            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <div className="flex-1 ml-64">

                {/* Navbar */}
                <Navbar />

                {/* Page Content */}
                <main className="p-8">
                    {children}
                </main>

            </div>

        </div>
    );
}

export default DashboardLayout;