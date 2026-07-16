import DashboardLayout from "../components/layout/DashboardLayout";
import StatCard from "../components/cards/StatCard";

import {
    FaMoneyBillWave,
    FaUsers,
    FaBuilding,
    FaHome
} from "react-icons/fa";

function Dashboard() {
    return (
        <DashboardLayout>

            <h1 className="text-3xl font-bold mb-8">
                Dashboard
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

                <StatCard
                    title="Total Revenue"
                    value="KSh"
                    icon={<FaMoneyBillWave />}
                    color="text-green-600"
                />

                <StatCard
                    title="Tenants"
                    value="48"
                    icon={<FaUsers />}
                    color="text-blue-600"
                />

                <StatCard
                    title="Occupied Units"
                    value="36"
                    icon={<FaBuilding />}
                    color="text-purple-600"
                />

                <StatCard
                    title="Vacant Units"
                    value="12"
                    icon={<FaHome />}
                    color="text-red-600"
                />

            </div>

        </DashboardLayout>
    );
}

export default Dashboard;